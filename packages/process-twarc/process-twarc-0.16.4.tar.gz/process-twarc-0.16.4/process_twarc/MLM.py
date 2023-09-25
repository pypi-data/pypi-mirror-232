
from transformers import Trainer, AutoTokenizer, AutoModelForMaskedLM, TrainingArguments, DataCollatorForLanguageModeling, TrainerCallback, EarlyStoppingCallback, get_linear_schedule_with_warmup
from torch.optim import AdamW
from torch.utils.data import DataLoader
from process_twarc.util import  load_dict, load_tokenizer, get_all_files, load_dataset, suggest_parameter, save_dict
from process_twarc.preprocess import tokenize_for_masked_language_modeling, collate_data
import torch
import wandb
import optuna
from ntpath import basename
import shutil
import os

class OptunaCallback(TrainerCallback):
    def __init__(self, trial, should_prune=True):
        self.trial = trial
        self.should_prune = should_prune

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        eval_loss = metrics.get("eval_loss")
        self.trial.report(eval_loss, step=state.global_step)
        if self.should_prune and self.trial.should_prune():
            raise optuna.TrialPruned()
        
class StopCallback(TrainerCallback):
    def on_epoch_end(self, args, state, control, logs=None, **kwargs):
        control.should_training_stop = True
        control.should_save = True
    
def initiate_trial(
    data_dir:str,
    path_to_tokenizer: str,
    path_to_model: str,
    checkpoint_dir: str,
    completed_dir: str,
    path_to_search_space: str,
    path_to_storage: str,
    print_details: bool=True,
    push_to_hub: bool=False,
    report_to: str="wandb"
):

    SEED = 42

    search_space = load_dict(path_to_search_space)
    project = search_space["meta"]["project"]
    group = search_space["meta"]["wandb_group"]
    study_name = search_space["meta"]["optuna_study"]

    base = lambda file_path: basename(file_path).split(".")[0]
    split_paths = [path for path in get_all_files(data_dir) if not base(path) == "test"]
    tokenized_datasets = {k:v for k,v in zip(
        [base(path) for path in split_paths],
        [load_dataset(path, output_type="Dataset") for path in split_paths]
    )}

    train_dataset = tokenized_datasets["train"]
    eval_dataset = tokenized_datasets["validation"]
    test_dataset = tokenized_datasets["development"]

    def objective(trial):

        trial_number = str(trial.number+1).zfill(3)
        trial_dir = f"{checkpoint_dir}/{study_name}/trial{trial_number}"
        complete_trial_dir = f"{completed_dir}/{study_name}/trial{trial_number}"

        run_name = f"{study_name}-{trial_number}"

        #Fixed Parameters
        PER_DEVICE_TRAIN_BATCH_SIZE = 55
        PER_DEVICE_EVAL_BATCH_SIZE = 75
        INTERVAL = 12
        EVAL_STRATEGY = "steps"
        SAVE_STRATEGY = "steps"
        METRIC_FOR_BEST_MODEL = "eval_loss"
        PATIENCE = 3
        LOGGING_STEPS = 500
        NUM_TRAIN_EPOCHS = 3
        NUM_WARMUP_STEPS = 10_000

        suggest = lambda param_name: suggest_parameter(trial, search_space, param_name)
        #Variable Parameters
        dropout_prob = suggest("dropout_prob")
        do_weight_decay = suggest("do_weight_decay")
        if do_weight_decay == True:
            weight_decay = suggest("weight_decay")
        else:
            weight_decay=0.0
        initial_learning_rate = suggest("initial_learning_rate")
        adam_beta1 = suggest("adam_beta1")
        adam_beta2 = suggest("adam_beta2")
        adam_epsilon = suggest("adam_epsilon")

        wandb_run_id = wandb.util.generate_id()
        wandb.init(
            project=project,
            group=group,  
            entity="lonewolfgang",
            name=run_name,
            id=wandb_run_id,
            resume="allow",
            config ={
            "meta": {
                "_name_or_path": "LoneWolfgang/bert-for-japanese-twitter"},
            "model":{
                "model_type": "bert",
                "hidden_act": "gelu",
                "hidden_size": 768,
                "num_hidden_layers": 12,
                "intermediate_size": 3072,
                "num_attention_heads": 12,
                "max_position_embeddings": 512,
                "position_embedding_type": "absolute",
                "vocab_size": 32_003,
                "initializer_range": 0.02,
                "attention_dropout_prob": dropout_prob,
                "hidden_dropout_prob": dropout_prob,
                "attention_probs_dropout_prob": dropout_prob,
                "weight_decay": weight_decay,
                "layer_norm_eps": 1e-12,
            },
            "optimizer":{
                "optim": "adamw_hf",
                "lr_scheduler_type": "linear",
                "initial_learning_rate": initial_learning_rate,
                "num_warmup_steps": NUM_WARMUP_STEPS,
                "adam_beta1": adam_beta1,
                "adam_beta2": adam_beta2,
                "adam_epsilon": adam_epsilon,
            },
            "trainer": {
                "num_train_epochs": NUM_TRAIN_EPOCHS,
                "logging_strategy": "steps",
                "logging_steps": LOGGING_STEPS,
                "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
                "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
                "eval_strategy": EVAL_STRATEGY,
                "eval_steps": len(train_dataset) // PER_DEVICE_TRAIN_BATCH_SIZE // INTERVAL,
                "save_strategy": SAVE_STRATEGY,
                "save_steps": len(train_dataset) // PER_DEVICE_TRAIN_BATCH_SIZE // INTERVAL,
                "patience": PATIENCE,
                "save_total_limit": INTERVAL,
                "metric_for_best_model": METRIC_FOR_BEST_MODEL,
                "seed": SEED
            }
        })

        fixed_params = {
            "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
            "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
            "num_train_epochs": NUM_TRAIN_EPOCHS,
            "num_warmup_steps": NUM_WARMUP_STEPS
        }

        variable_params = {
            "dropout_prob": dropout_prob,
            "weight_decay": weight_decay,
            "initial_learning_rate": initial_learning_rate,
            "adam_beta1": adam_beta1,
            "adam_beta2": adam_beta2,
            "adam_epsilon": adam_epsilon
        }
    
        print("Variable Params:")
        for key, value in variable_params.items():
            print(f"{key}: {value}")

        print("\nFixed Params:")
        for key, value in fixed_params.items():
            print(f"{key}: {value}")

        device = "cuda" if torch.cuda.is_available() else RuntimeError("No GPU available.")

        tokenizer = load_tokenizer(path_to_tokenizer, AutoTokenizer, print_details=print_details)
        model = AutoModelForMaskedLM.from_pretrained(path_to_model)
        model.config.hidden_dropout_prob = dropout_prob
        model.config.attention_dropout_prob = dropout_prob
        model.config.attention_probs_dropout_prob = dropout_prob
        model.to(device)
        
        if print_details:
            print(model.config)

        data_collator = collate_data(DataCollatorForLanguageModeling, tokenizer, train_dataset, PER_DEVICE_TRAIN_BATCH_SIZE)

        optimizer = AdamW(
            params=model.parameters(),
            lr=initial_learning_rate,
            betas = (adam_beta1, adam_beta2),
            eps=adam_epsilon,
            weight_decay=weight_decay)
        
        scheduler = get_linear_schedule_with_warmup(
            optimizer=optimizer,
            num_warmup_steps=NUM_WARMUP_STEPS,
            num_training_steps=len(train_dataset)//PER_DEVICE_TRAIN_BATCH_SIZE * NUM_TRAIN_EPOCHS,
            last_epoch = -1
        )

        training_args = TrainingArguments(
            lr_scheduler_type="linear",
            logging_steps=LOGGING_STEPS,
            warmup_steps= NUM_WARMUP_STEPS,
            learning_rate=initial_learning_rate,
            adam_beta1=adam_beta1,
            adam_beta2=adam_beta2,
            adam_epsilon=adam_epsilon,
            weight_decay=weight_decay,
            output_dir=trial_dir,
            evaluation_strategy=EVAL_STRATEGY,
            eval_steps= 1 / INTERVAL / NUM_TRAIN_EPOCHS,
            num_train_epochs=NUM_TRAIN_EPOCHS,
            save_strategy=SAVE_STRATEGY,
            save_steps=1 / INTERVAL /NUM_TRAIN_EPOCHS,
            save_total_limit=PATIENCE,
            push_to_hub=push_to_hub,
            per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH_SIZE,
            load_best_model_at_end=True, 
            metric_for_best_model=METRIC_FOR_BEST_MODEL,
            report_to=report_to
        )
        
        custom_args = {
            "wandb_run_id": wandb_run_id,
            "last_train_epoch": 0,
            "patience": PATIENCE,
            "interval": INTERVAL
        }

        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            optimizers=(optimizer, scheduler),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=PATIENCE),
                       StopCallback()]
        )

        trainer.train()
        #Return the results of the final evaulation

        custom_args["last_train_epoch"] = trainer.state.epoch
        # checks to see if the EarlStoppingCallback was triggered by checking if trainer.state.epoch is divisible by 1
        if trainer.state.epoch%1 != 0:
            print("EarlyStoppingCallback triggered.")
            results = trainer.evaluate(test_dataset)
            print("\nResults:", results)
            wandb.log(results)
            trainer.save_model(complete_trial_dir)
            save_dict(custom_args, f"{complete_trial_dir}/custom_args.json")
            #deletes the trial directory
            shutil.rmtree(trial_dir)
        
        else:
            print(f"Training paused. Last train epoch: {custom_args['last_train_epoch']}.")
            save_dict(custom_args, f"{trial_dir}/custom_args.json")
        
        return 1
    
    study_name = search_space["meta"]["optuna_study"]
    study = optuna.create_study(
        storage=path_to_storage,
        sampler=optuna.samplers.RandomSampler(),
        study_name=study_name,
        direction="minimize",
        load_if_exists=True,
        )
    study.optimize(objective, n_trials=1)


def resume_trial(
    data_dir:str,
    path_to_tokenizer: str,
    path_to_model: str,
    path_to_search_space: str,
    trial_dir: str,
    completed_dir: str,
    device = "cuda" if torch.cuda.is_available() else RuntimeError("No GPU available."),
    print_details: bool=True,
):
    def get_last_checkpoint(trial_dir: str):
        checkpoints = [os.path.join(trial_dir, checkpoint) for checkpoint in os.listdir(trial_dir) if os.path.isdir(os.path.join(trial_dir, checkpoint))]
        return max(checkpoints, key=os.path.getctime)
    
    checkpoint_dir = get_last_checkpoint(trial_dir)

    search_space = load_dict(path_to_search_space)
    project = search_space["meta"]["project"]
    
    base = lambda file_path: basename(file_path).split(".")[0]
    split_paths = [path for path in get_all_files(data_dir) if not base(path) == "test"]
    tokenized_datasets = {k:v for k,v in zip(
        [base(path) for path in split_paths],
        [load_dataset(path, output_type="Dataset") for path in split_paths]
    )}

    completed_trial_dir = f"{completed_dir}/{basename(trial_dir)}"

    tokenizer = load_tokenizer(path_to_tokenizer, AutoTokenizer, print_details=print_details)

    train_dataset = tokenized_datasets["train"]
    eval_dataset = tokenized_datasets["validation"]
    test_dataset = tokenized_datasets["development"]

    model = AutoModelForMaskedLM.from_pretrained(path_to_model).to(device)

    training_args = torch.load(f"{checkpoint_dir}/training_args.bin")
    custom_args = load_dict(f"{trial_dir}/custom_args.json")

    #Fixed Parameters
    PER_DEVICE_TRAIN_BATCH_SIZE = training_args.per_device_train_batch_size
    PER_DEVICE_EVAL_BATCH_SIZE = training_args.per_device_eval_batch_size
    NUM_TRAIN_EPOCHS = training_args.num_train_epochs
    NUM_WARMUP_STEPS = training_args.warmup_steps
    LAST_TRAIN_EPOCH = custom_args["last_train_epoch"]

    if LAST_TRAIN_EPOCH + 1 == NUM_TRAIN_EPOCHS:
        final_epoch = True
    else:
        final_epoch = False

    #Variable Parameters
    dropout_prob = model.config.hidden_dropout_prob
    weight_decay = training_args.weight_decay
    initial_learning_rate = training_args.learning_rate
    adam_beta1 = training_args.adam_beta1
    adam_beta2 = training_args.adam_beta2
    adam_epsilon = training_args.adam_epsilon


    fixed_params = {
    "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
    "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
    "num_train_epochs": NUM_TRAIN_EPOCHS,
    "last_train_epoch": LAST_TRAIN_EPOCH,
    "num_warmup_steps": NUM_WARMUP_STEPS,
    }

    variable_params = {
        "dropout_prob": dropout_prob,
        "weight_decay": weight_decay,
        "initial_learning_rate": initial_learning_rate,
        "adam_beta1": adam_beta1,
        "adam_beta2": adam_beta2,
        "adam_epsilon": adam_epsilon
    }

    print("Variable Params:")
    for key, value in variable_params.items():
        print(f"{key}: {value}")

    print("\nFixed Params:")
    for key, value in fixed_params.items():
        print(f"{key}: {value}")

    wandb.init(
        project=project,
        id=custom_args["wandb_run_id"],
        resume="must")
    
    data_collator = collate_data(DataCollatorForLanguageModeling, tokenizer, train_dataset, PER_DEVICE_TRAIN_BATCH_SIZE)

    optimizer = AdamW(
        params=model.parameters(),
        lr=initial_learning_rate,
        betas = (adam_beta1, adam_beta2),
        eps=adam_epsilon,
        weight_decay=weight_decay)
    optimizer.load_state_dict(torch.load(f"{checkpoint_dir}/optimizer.pt"))

    scheduler = get_linear_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=NUM_WARMUP_STEPS,
        num_training_steps=len(train_dataset)//PER_DEVICE_TRAIN_BATCH_SIZE * NUM_TRAIN_EPOCHS,
        last_epoch = custom_args["last_train_epoch"])
    scheduler.load_state_dict(torch.load(f"{checkpoint_dir}/scheduler.pt"))

    if final_epoch:
        callbacks = [EarlyStoppingCallback(early_stopping_patience=custom_args["patience"])]
    else:
        callbacks = [EarlyStoppingCallback(early_stopping_patience=custom_args["patience"]),
                        StopCallback()]

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        optimizers=(optimizer, scheduler),
        callbacks=callbacks
    )

    trainer.train(resume_from_checkpoint=checkpoint_dir)

    custom_args["last_train_epoch"] = trainer.state.epoch
    # checks to see if the EarlStoppingCallback was triggered
    if trainer.state.epoch%1 != 0:
        print("EarlyStoppingCallback triggered.")
        results = trainer.evaluate(test_dataset)
        print("\nResults:", results)
        wandb.log(results)
        trainer.save_model(completed_trial_dir)
        save_dict(custom_args, f"{completed_trial_dir}/custom_args.json")
        #deletes the trial directory
        shutil.rmtree(trial_dir)

    elif trainer.state.epoch == NUM_TRAIN_EPOCHS:
        print("Training complete.")
        results = trainer.evaluate(test_dataset)
        print("\nResults:", results)
        wandb.log(results)
        trainer.save_model(completed_trial_dir)
        save_dict(custom_args, f"{completed_trial_dir}/custom_args.json")
        #deletes the trial directory
        shutil.rmtree(trial_dir)

    else:
        print(f"Training paused. Last train epoch: {custom_args['last_train_epoch']}.")
        save_dict(custom_args, f"{trial_dir}/custom_args.json")

    return

def MLM_sweep(
    data_dir: str,
    path_to_tokenizer: str,
    path_to_model: str,
    checkpoint_dir: str,
    path_to_search_space: str,
    path_to_storage: str,
    n_trials: int=1,
    enable_pruning: bool=False,
    push_to_hub: bool=False,
    print_details: bool=True,
    report_to: str="wandb"
):

    SEED = 42

    search_space = load_dict(path_to_search_space)

    base = lambda file_path: basename(file_path).split(".")[0]
    split_paths = [path for path in get_all_files(data_dir) if base(path) != "test"]
    tokenized_datasets = {k:v for k,v in zip(
        [base(path) for path in split_paths],
        [load_dataset(path, output_type="Dataset") for path in split_paths]
    )}

    train_dataset = tokenized_datasets["train"]
    eval_dataset = tokenized_datasets["validation"]
    test_dataset = tokenized_datasets["development"]

    def objective(trial):

        trial_number = str(trial.number+1).zfill(3)
        project = search_space["meta"]["project"]
        group = search_space["meta"]["wandb_group"]
        study_name = search_space["meta"]["optuna_study"]
        trial_dir = f"{checkpoint_dir}/{study_name}/trial{trial_number}"
        run_name = f"{study_name}-{trial_number}"

        #Fixed Parameters
        PER_DEVICE_TRAIN_BATCH_SIZE = 55
        PER_DEVICE_EVAL_BATCH_SIZE = 75
        INTERVAL = 12
        EVAL_STRATEGY = "steps"
        SAVE_STRATEGY = "steps"
        METRIC_FOR_BEST_MODEL = "eval_loss"
        PATIENCE = 4
        LOGGING_STEPS = 500
        
        #Variable Parameters
        dropout_prob=suggest_parameter("dropout_prob")
        do_weight_decay=suggest_parameter("do_weight_decay")
        if do_weight_decay == True:
            weight_decay=suggest_parameter("weight_decay")
        else:
            weight_decay=0.0
        num_train_epochs=suggest_parameter("num_train_epochs")
        initial_learning_rate=suggest_parameter("initial_learning_rate")
        num_warmup_steps=suggest_parameter("num_warmup_steps")
        power=suggest_parameter("power")
        adam_beta1=suggest_parameter("adam_beta1")
        adam_beta2=suggest_parameter("adam_beta2")
        adam_epsilon=suggest_parameter("adam_epsilon")

        wandb.init(
            project=project,
            group=group,  
            entity="lonewolfgang",
            name=run_name,
            config ={
            "meta": {
                "_name_or_path": "LoneWolfgang/bert-for-japanese-twitter"},
            "model":{
                "model_type": "bert",
                "hidden_act": "gelu",
                "hidden_size": 768,
                "num_hidden_layers": 12,
                "intermediate_size": 3072,
                "num_attention_heads": 12,
                "max_position_embeddings": 512,
                "position_embedding_type": "absolute",
                "vocab_size": 32_003,
                "initializer_range": 0.02,
                "attention_dropout_prob": dropout_prob,
                "hidden_dropout_prob": dropout_prob,
                "attention_probs_dropout_prob": dropout_prob,
                "weight_decay": weight_decay,
                "layer_norm_eps": 1e-12,
            },
            "optimizer":{
                "optim": "adamw_hf",
                "lr_scheduler_type": "linear",
                "initial_learning_rate": initial_learning_rate,
                "num_warmup_steps": num_warmup_steps,
                "adam_beta1": adam_beta1,
                "adam_beta2": adam_beta2,
                "adam_epsilon": adam_epsilon,
            },
            "trainer": {
                "num_train_epochs": num_train_epochs,
                "logging_strategy": "steps",
                "logging_steps": LOGGING_STEPS,
                "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE,
                "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
                "eval_strategy": EVAL_STRATEGY,
                "eval_steps": len(train_dataset) // PER_DEVICE_TRAIN_BATCH_SIZE // INTERVAL,
                "save_strategy": SAVE_STRATEGY,
                "save_steps": len(train_dataset) // PER_DEVICE_TRAIN_BATCH_SIZE // INTERVAL,
                "patience": PATIENCE,
                "save_total_limit": INTERVAL,
                "metric_for_best_model": METRIC_FOR_BEST_MODEL,
                "seed": SEED
            }
        })

        fixed_params = {
            "per_device_train_batch_size": PER_DEVICE_TRAIN_BATCH_SIZE,
            "per_device_eval_batch_size": PER_DEVICE_EVAL_BATCH_SIZE
        }

        variable_params = {
            "hidden_dropout_prob": dropout_prob,
            "attention_dropout_prob": dropout_prob,
            "attention_probs_dropout_prob": dropout_prob,
            "weight_decay": weight_decay,
            "num_train_epochs": num_train_epochs,
            "initial_learning_rate": initial_learning_rate,
            "num_warmup_steps": num_warmup_steps,
            "power": power,
            "adam_beta1": adam_beta1,
            "adam_beta2": adam_beta2,
            "adam_epsilon": adam_epsilon
        }
    
        print("\nVariable Params:")
        for key in variable_params:
            print(key, variable_params[key])
        print("\nFixed Params:")
        for key in fixed_params:
            print(key, fixed_params[key])

        device = "cuda" if torch.cuda.is_available() else RuntimeError("No GPU available.")

        tokenizer = load_tokenizer(path_to_tokenizer, AutoTokenizer, print_details=print_details)
        model = AutoModelForMaskedLM.from_pretrained(path_to_model)
        model.config.hidden_dropout_prob = dropout_prob,
        model.config.attention_dropout_prob = dropout_prob
        model.config.attention_probs_dropout_prob = dropout_prob
        model.to(device)
        
        if print_details:
            print(model.config)

        data_collator = collate_data(DataCollatorForLanguageModeling, tokenizer, train_dataset, PER_DEVICE_TRAIN_BATCH_SIZE)

        optimizer = AdamW(
            params=model.parameters(),
            lr=initial_learning_rate,
            betas = (adam_beta1, adam_beta2),
            eps=adam_epsilon,
            weight_decay=weight_decay)
        
        scheduler = get_linear_schedule_with_warmup(
            optimizer=optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=len(train_dataset)//PER_DEVICE_TRAIN_BATCH_SIZE * num_train_epochs
        )

        training_args = TrainingArguments(
            lr_scheduler_type="linear",
            learning_rate=initial_learning_rate,
            adam_beta1=adam_beta1,
            adam_beta2=adam_beta2,
            adam_epsilon=adam_epsilon,
            weight_decay=weight_decay,
            output_dir=trial_dir,
            evaluation_strategy=EVAL_STRATEGY,
            eval_steps= 1 / INTERVAL / num_train_epochs,
            num_train_epochs=num_train_epochs,
            save_strategy=SAVE_STRATEGY,
            save_steps=1 / INTERVAL /num_train_epochs,
            save_total_limit=INTERVAL,
            push_to_hub=push_to_hub,
            per_device_train_batch_size=PER_DEVICE_TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=PER_DEVICE_EVAL_BATCH_SIZE,
            load_best_model_at_end=True, 
            metric_for_best_model=METRIC_FOR_BEST_MODEL,
            report_to=report_to
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=tokenizer,
            optimizers=(optimizer, scheduler),
            callbacks=[EarlyStoppingCallback(early_stopping_patience=PATIENCE),
                       OptunaCallback(trial, should_prune=enable_pruning)]
        )
        trainer.train()
        results = trainer.evaluate(test_dataset)
        print("\nResults:", results)
        wandb.log(results)
        trainer.save_model()

        return results["eval_loss"]
    
    
    study_name = search_space["meta"]["optuna_study"]
    study = optuna.create_study(
        storage=path_to_storage,
        sampler=optuna.samplers.RandomSampler(seed=SEED),
        pruner=optuna.pruners.MedianPruner(n_warmup_steps=12, interval_steps=3, n_min_trials=10),
        study_name=study_name,
        direction="minimize",
        load_if_exists=True,
        )
    study.optimize(objective, n_trials=n_trials)

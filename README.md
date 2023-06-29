# KISusCheck

## Run Rasa

```
1- open .env file and add this key "OPENAI_API_KEY='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'"

2- cd Rasa directory folder

3- Open 2 Anaconda Prompts

4- Run “rasa run --cors "*" --enable-api” command in the first terminal

5- Run “rasa run actions” command in the second terminal
```

## Run Frontend

```
1- cd frontend directory folder

2- run "npm i" command in the terminal

3- run "npm start" command in the terminal
```

## Activate virtual env on VM

1. activate `eduVPN`.

2.

```
ssh -i your/path/to/kisuscheck-rasa-key.txt ubuntu@10.195.4.92
```

3.

```
source ~/.venv/bin/activate
```

4.

```
cd Rasa
```

Then use `rasa` command normaly.

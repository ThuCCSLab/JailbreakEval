# Development Guide
## Setting Up Your Development Environment

Use the following command to clone the repository and install the development dependencies.
```shell
git clone https://github.com/ThuCCSLab/JailbreakEval
cd JailbreakEval
make dev
```

Now, you're all set to start developing!

## Debugging with Visual Studio Code
For those who prefer using Visual Studio Code, you can debug this project as a module.

Here is a sample `launch.json` for debugging CLI:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Module",
            "type": "debugpy",
            "request": "launch",
            "module": "jailbreakeval.commands.main",
            "args": [
                // args of CLI
                "--dataset=data/example.csv",
                "StringMatching-zou2023universal",
            ]
        }
    ]
}
``` 

## Runnning Tests
This project utilizes `pytest` as its testing framework. All tests are located in the `tests/` directory, and you can run them with:
```shell
make test
```
Note: The tests rely on certain Hugging Face models. If you're unable to access Hugging Face directly, you can download them manually and set the corresponding environment variables as shown below:
```shell
TEST_CLASSIFICATION_MODEL=path/to/Elron/bleurt-tiny-512 \
TEST_CHAT_MODEL=path/to/trl-internal-testing/tiny-random-LlamaForCausalLM \
make test
```

Alternatively, you may use a unofficial mirror for Hugging Face by setting the `HF_ENDPOINT` environment variable:
```shell
HF_ENDPOINT=https://hf-mirror.com \
make test
```

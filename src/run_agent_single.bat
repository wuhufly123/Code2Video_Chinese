@echo off
setlocal enabledelayedexpansion

:: ========== 1) Default values and constants ==========
set "API=claude"
set "FOLDER_PREFIX=TEST-single"

:: Hyperparameters
set "MAX_CODE_TOKEN_LENGTH=10000"
set "MAX_FIX_BUG_TRIES=10"
set "MAX_REGENERATE_TRIES=10"
set "MAX_FEEDBACK_GEN_CODE_TRIES=3"
set "MAX_MLLM_FIX_BUGS_TRIES=3"
set "FEEDBACK_ROUNDS=2"

set "DEFAULT_KNOWLEDGE_POINT=Linear transformations and matrices"
set "KNOWLEDGE_POINT_ARGS="

:: ========== 2) Check if --knowledge_point is provided ==========
set "found_kp=0"
set "args=%*"
for %%a in (%*) do (
    if /i "%%a"=="--knowledge_point" (
        set "found_kp=1"
    )
)

if %found_kp% EQU 0 (
    echo INFO: Using default knowledge point: %DEFAULT_KNOWLEDGE_POINT%
    set "KNOWLEDGE_POINT_ARGS=--knowledge_point "%DEFAULT_KNOWLEDGE_POINT%""
)

:: ========== 3) Execute ==========
python agent.py ^
  --API "%API%" ^
  --folder_prefix "%FOLDER_PREFIX%" ^
  --use_feedback ^
  --use_assets ^
  --max_code_token_length "%MAX_CODE_TOKEN_LENGTH%" ^
  --max_fix_bug_tries "%MAX_FIX_BUG_TRIES%" ^
  --max_regenerate_tries "%MAX_REGENERATE_TRIES%" ^
  --max_feedback_gen_code_tries "%MAX_FEEDBACK_GEN_CODE_TRIES%" ^
  --max_mllm_fix_bugs_tries "%MAX_MLLM_FIX_BUGS_TRIES%" ^
  --feedback_rounds "%FEEDBACK_ROUNDS%" ^
  --parallel ^
  %KNOWLEDGE_POINT_ARGS% ^
  %*
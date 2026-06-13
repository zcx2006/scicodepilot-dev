理论上是一次性测试10组数据，但是实际测试时发现每次只能通过大约3组，其余组全部显示failed

模型名及调用名：
DeepSeek V3.2：调用名 deepseek-chat 或  deepseek-reasoner
GLM 5.0：调用名 glm-5
MiniMax M2.5：调用名 minimax 或 minimax-m2.5
Qwen3-Coder-30B：调用名 qwen3coder
Qwen3-VL-32B：调用名 qwen3vl

API Base_url: https://models.sjtu.edu.cn/api/v1

Summary_10_Tasks是10组success的汇总
以下为记录：

repair_tensor_shape_001 | structured_patchplan | success
repair_tensor_shape_001 | structured_patchplan_with_memory | success
repair_dtype_mismatch_002 | direct_llm | success
repair_dtype_mismatch_002 | structured_patchplan | success
repair_dtype_mismatch_002 | structured_patchplan_with_memory | success
repair_missing_module_003 | direct_llm | success
repair_missing_module_003 | structured_patchplan | success
repair_missing_module_003 | structured_patchplan_with_memory | success
repair_missing_file_004 | direct_llm | success
repair_missing_file_004 | structured_patchplan | failed
repair_missing_file_004 | structured_patchplan_with_memory | failed
repair_entrypoint_error_005 | direct_llm | failed
repair_entrypoint_error_005 | structured_patchplan | failed
repair_entrypoint_error_005 | structured_patchplan_with_memory | failed
repair_label_shape_006 | direct_llm | failed
repair_label_shape_006 | structured_patchplan | failed
repair_label_shape_006 | structured_patchplan_with_memory | failed
repair_device_mismatch_007 | direct_llm | failed
repair_device_mismatch_007 | structured_patchplan | failed
repair_device_mismatch_007 | structured_patchplan_with_memory | failed
repair_loss_input_008 | direct_llm | failed
repair_loss_input_008 | structured_patchplan | failed
repair_loss_input_008 | structured_patchplan_with_memory | failed
repair_collate_fn_009 | direct_llm | failed
repair_collate_fn_009 | structured_patchplan | failed
repair_collate_fn_009 | structured_patchplan_with_memory | failed
repair_config_key_010 | direct_llm | failed
repair_config_key_010 | structured_patchplan | failed
repair_config_key_010 | structured_patchplan_with_memory | failed

Saved outputs to: D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main\outputs\m30_llm_smoke\20260609_204733

Liu@LYS MINGW64 /d/Git/My_Git_Project/SciCodePilot/M30_Work
$ python /d/Git/My_Git_Project/SciCodePilot/M30_Work/m30_sjtu_llm_smoke_all10.py
repair_missing_file_004 | direct_llm | success
repair_missing_file_004 | structured_patchplan | success
repair_missing_file_004 | structured_patchplan_with_memory | success
repair_entrypoint_error_005 | direct_llm | success
repair_entrypoint_error_005 | structured_patchplan | success
repair_entrypoint_error_005 | structured_patchplan_with_memory | success
repair_label_shape_006 | direct_llm | success
repair_label_shape_006 | structured_patchplan | success
repair_label_shape_006 | structured_patchplan_with_memory | success
repair_device_mismatch_007 | direct_llm | success
repair_device_mismatch_007 | structured_patchplan | failed
repair_device_mismatch_007 | structured_patchplan_with_memory | failed
repair_loss_input_008 | direct_llm | failed
repair_loss_input_008 | structured_patchplan | failed
repair_loss_input_008 | structured_patchplan_with_memory | failed
repair_collate_fn_009 | direct_llm | failed
repair_collate_fn_009 | structured_patchplan | failed
repair_collate_fn_009 | structured_patchplan_with_memory | failed
repair_config_key_010 | direct_llm | failed
repair_config_key_010 | structured_patchplan | failed
repair_config_key_010 | structured_patchplan_with_memory | failed

Saved outputs to: D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main\outputs\m30_llm_smoke\20260609_205013

Liu@LYS MINGW64 /d/Git/My_Git_Project/SciCodePilot/M30_Work
$ python /d/Git/My_Git_Project/SciCodePilot/M30_Work/m30_sjtu_llm_smoke_all10.py
repair_device_mismatch_007 | direct_llm | success
repair_device_mismatch_007 | structured_patchplan | success
repair_device_mismatch_007 | structured_patchplan_with_memory | success
repair_loss_input_008 | direct_llm | failed
repair_loss_input_008 | structured_patchplan | success
repair_loss_input_008 | structured_patchplan_with_memory | failed
repair_collate_fn_009 | direct_llm | failed
repair_collate_fn_009 | structured_patchplan | failed
repair_collate_fn_009 | structured_patchplan_with_memory | failed

Saved outputs to: D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main\outputs\m30_llm_smoke\20260609_205124

Liu@LYS MINGW64 /d/Git/My_Git_Project/SciCodePilot/M30_Work
$ ^[[200~python /d/Git/My_Git_Project/SciCodePilot/M30_Work/m30_sjtu_llm_smoke_all10.py~
bash: $'\E[200~python': command not found

Liu@LYS MINGW64 /d/Git/My_Git_Project/SciCodePilot/M30_Work
$ python /d/Git/My_Git_Project/SciCodePilot/M30_Work/m30_sjtu_llm_smoke_all10.py
repair_loss_input_008 | direct_llm | success
repair_loss_input_008 | structured_patchplan | success
repair_loss_input_008 | structured_patchplan_with_memory | success
repair_collate_fn_009 | direct_llm | success
repair_collate_fn_009 | structured_patchplan | success
repair_collate_fn_009 | structured_patchplan_with_memory | success

Saved outputs to: D:\Git\My_Git_Project\SciCodePilot\scicodepilot-dev-main\outputs\m30_llm_smoke\20260609_205215


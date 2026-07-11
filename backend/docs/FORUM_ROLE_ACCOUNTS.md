# 论坛身份账号维护

`forum_role` 与系统权限 `role` 独立：前者只在登录用户浏览论坛时显示“老师”或“代班”标签，不赋予额外权限。

使用本地受控脚本创建或更新账号。身份证号会交互式输入，不会出现在命令行历史中：

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\manage_student_account.py --student-id teacher-001 --name 张老师 --class-name 教务处 --system-role admin --forum-role teacher
.\.venv\Scripts\python.exe scripts\manage_student_account.py --student-id assistant-001 --name 李同学 --class-name 软件工程2026-1班 --system-role student --forum-role assistant
.\.venv\Scripts\python.exe scripts\manage_student_account.py --student-id assistant-001 --forum-role none
```

- `--forum-role teacher`：显示“老师”标签。
- `--forum-role assistant`：显示“代班”标签。
- `--forum-role none`：清除论坛身份。
- 不传 `--forum-role`：保留现有论坛身份。

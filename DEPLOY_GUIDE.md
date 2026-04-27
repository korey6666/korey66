# 房价预测网站 - Vercel 部署指南

## 项目概述
这是一个基于决策树模型的房价预测Web应用，使用Flask框架开发。

## 部署前准备

### 1. 安装必要工具

#### Windows用户：
1. **安装Git**：https://git-scm.com/download/win
2. **安装Node.js**（包含npm）：https://nodejs.org/ （下载LTS版本）
3. **注册Vercel账号**：https://vercel.com/signup （建议使用GitHub账号登录）

#### 验证安装：
```bash
git --version
node --version
npm --version
```

### 2. 安装Vercel CLI
```bash
npm install -g vercel
```

验证安装：
```bash
vercel --version
```

## 部署步骤

### 步骤1：初始化Git仓库

在项目目录下打开命令行，执行：

```bash
cd "d:\QQ\数据集"
git init
```

### 步骤2：创建.gitignore文件

创建 `.gitignore` 文件，内容如下：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
debug.log

# Data (可选，如果数据文件太大)
# data/
# *.csv
```

### 步骤3：提交代码

```bash
# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: House price prediction app"
```

### 步骤4：创建GitHub仓库并推送

1. 访问 https://github.com/new 创建新仓库
2. 仓库名称建议：`house-price-prediction`
3. 不要初始化README（因为本地已有代码）
4. 创建后，按照页面提示推送代码：

```bash
# 添加远程仓库（替换YOUR_USERNAME为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/house-price-prediction.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤5：部署到Vercel

#### 方式A：使用Vercel CLI（推荐）

```bash
# 登录Vercel
vercel login

# 部署
vercel

# 按照提示操作：
# - 确认项目路径
# - 选择或创建Vercel项目
# - 等待部署完成

# 生产环境部署
vercel --prod
```

部署完成后，Vercel会提供一个URL，例如：
`https://house-price-prediction-xxx.vercel.app`

#### 方式B：通过GitHub集成（更简单）

1. 访问 https://vercel.com/new
2. 选择 "Import Git Repository"
3. 选择你的GitHub仓库 `house-price-prediction`
4. Vercel会自动检测配置并部署
5. 每次推送代码到GitHub，Vercel会自动重新部署

## 项目结构说明

```
d:\QQ\数据集\
├── api/
│   └── index.py          # Vercel Serverless入口文件
├── models/               # 训练好的模型文件
│   ├── decision_tree_model.pkl
│   ├── label_encoder.pkl
│   └── model_info.json
├── outputs/              # 分析结果和可视化
│   ├── analysis/
│   ├── model/
│   └── test_analysis/
├── web/
│   └── templates/        # HTML模板
│       ├── base.html
│       ├── index.html
│       ├── predict.html
│       └── results.html
├── vercel.json           # Vercel配置文件
├── requirements.txt      # Python依赖
└── DEPLOY_GUIDE.md       # 本指南
```

## 配置文件说明

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/outputs/test_analysis/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### requirements.txt
```
flask==3.0.0
pandas==2.1.4
numpy==1.26.2
scikit-learn==1.3.2
matplotlib==3.8.2
seaborn==0.13.0
```

## 常见问题

### 1. 模型文件太大
如果模型文件超过50MB，Vercel会报错。解决方案：
- 使用更简单的模型
- 或者使用其他平台如PythonAnywhere

### 2. 部署失败
检查：
- `vercel.json` 配置是否正确
- `requirements.txt` 是否包含所有依赖
- `api/index.py` 路径是否正确

### 3. 静态文件无法访问
确保 `vercel.json` 中的路由配置正确。

## 部署后验证

访问部署后的URL，检查以下页面：
- 首页：`https://your-app.vercel.app/`
- 预测页面：`https://your-app.vercel.app/predict`
- 结果页面：`https://your-app.vercel.app/results`

## 更新部署

修改代码后，重新部署：

```bash
# 提交更改
git add .
git commit -m "Update: xxx"
git push

# 如果使用CLI，手动部署
vercel --prod
```

如果使用GitHub集成，推送代码后会自动重新部署。

## 手机访问

部署成功后，任何设备都可以通过URL访问：
- 手机浏览器
- 平板
- 其他电脑

---

**需要帮助？**
- Vercel文档：https://vercel.com/docs
- Flask文档：https://flask.palletsprojects.com/

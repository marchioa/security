# Data Security

Materials, notebooks, and supporting Python code for [90392 - ELEMENTS OF APPLIED DATA SECURITY M](https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/2025/443929) and [B8311 - SECURITY OF DATA AND NEURAL PROCESSING M](https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/2025/542497).

This repository is designed to work in:
- ✅ Google Colab (no installation required)
- ✅ Local environments using JupyterLab or VS Code

The same notebooks run in both environments.


## 🚀 Quick Start

Choose **one** of the following options.
- A. Run in [Google Colab](https://colab.research.google.com/) (Recommended for beginners)
- B. Run Locally ([JupyterLab](https://jupyter.org/) or [Visual Studio Code](https://code.visualstudio.com/))

### Option A — Run in Google Colab


#### Open a notebook

Go to https://colab.research.google.com

1. Click File → Open notebook
2. Select the GitHub tab
3. Paste https://github.com/marchioa/security
4. Click the `.ipynb` notebook you want.

Colab will load the notebook and run it in its own environment.


Alternatively, you can directly open from GitHub using URL trick (very fast). Just replace `github.com` with `colab.research.google.com/github`.
For instance, if your notebook is at `https://github.com/user/repo/blob/branch/notebook.ipynb`, change the URL to
`https://colab.research.google.com/github/user/repo/blob/branch/notebook.ipynb`.


#### Install required packages

In case the notebook needs some packages that are not available in the default Colab environment, you will find a **first setup cell** to be run:
```python
!pip install -q git+https://github.com/marchioa/security.git
```
This installs all required packages automatically.


### Option B — Run Locally

#### 1. Install Conda

We recommend managing Python and course dependencies using Conda.

[Conda](https://docs.conda.io/projects/conda/en/latest/index.html) is an open-source environment and package manager that runs on Windows, macOS, and Linux. It allows you to create isolated environments containing a specific Python version and all required libraries for a project.

Using Conda helps avoid common installation problems and ensures that everyone runs the course materials in a consistent and reproducible setup.

Conda allows you to:
- install and update packages together with their dependencies
- create separate environments for different projects
- switch safely between environments without conflicts
- manage multiple Python versions on the same computer

Although widely used for Python, Conda can also manage packages for many languages, including R, C/C++, Java, and others.

We recommend installing conda through [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main), a lightweight Conda distribution. Follow Miniconda [installation guide](https://www.anaconda.com/docs/getting-started/miniconda/install).

#### 2. Create a Python Environment

After installing Conda, create a dedicated environment for the course.
Using a separate environment prevents conflicts with other Python projects on your computer.

Open a terminal (or *Anaconda Prompt* on Windows) and run:
```bash
conda create -n <env-name> python=3.11
```
where `<env-name>` must be replaced with the name you want to use for the environment (e.g., `security`).

Activate the environment:
```bash
conda activate <env-name>
```
Your terminal prompt should now show `(<env-name>)`.


#### 3. Clone the course repository

Clone the repository:
```bash
git clone https://github.com/marchioa/security.git
cd security
```


#### 4. Install the course package

Install the repository and its dependencies:
```bash
pip install -e ".[notebook]"
```

This command:
- installs all required Python packages
- makes the `security` module available for import
- keeps the installation linked to the repository (changes update automatically)


#### 5. Open a notebook and select a Python kernel

You can open a jupyter notebook from either **VSCode** or **JupyterLab**.

You can start JupyterLab from your terminal (or *Anaconda Prompt* on Windows)
```bash
jupyter lab
```

Then open a notebook from the `notebooks/` folder and select the kernel:
```
Python (<env-name>)
```


## 🔄 Updating the Environment

When the course repository is updated:
```bash
git pull
pip install -e .
```
This refreshes dependencies while keeping your environment intact.


## 📁 Repository Structure

```
security/
│
├── notebooks/       # Lectures and exercises
├── src/             # Reusable Python modules
├── pyproject.toml   # Dependencies and configuration
└── README.md
```


## 💾 Saving Your Work

### In Colab

Use: `File → Save a copy in Drive`

### Locally

Work directly inside your cloned repository.


## 📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

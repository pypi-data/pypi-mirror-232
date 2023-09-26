import os
import subprocess
import nbformat as nbf

class AkreModel:
    
    @classmethod
    def create_empty_notebook(output_file):
        # Create a new Jupyter notebook
        nb = nbf.v4.new_notebook()
        nb['cells'] = [nbf.v4.new_markdown_cell("## Write your script here")]

        # Write the notebook to a file
        with open(output_file, 'w') as f:
            nbf.write(nb, f)

    @classmethod
    def create_model(app_name):
        # Create project directory
        os.makedirs(app_name)
        os.chdir(app_name)

        # Initialize virtual environment
        subprocess.run(["python", "-m", "venv", "venv"])

        os.makedirs("preprocess")
        os.makedirs("models")
        os.makedirs("postprocess")


        # Create requirements.txt
        with open("requirements.txt", "w") as f:
            f.write("# Add your dependencies here")

        # Create README.md
        with open("README.md", "w") as f:
            f.write(f"# {app_name}\n\nDescription of your project goes here.")

        os.chdir("preprocess")
        AkreModel.create_empty_notebook('preprocess.ipynb')
        os.chdir("../postprocess")
        AkreModel.create_empty_notebook('postprocess.ipynb')

        print(f"Project '{app_name}' created successfully.")
        
    if __name__ == "__main__":
        app_name = input("Enter the name of your project: ")
        create_model(app_name)

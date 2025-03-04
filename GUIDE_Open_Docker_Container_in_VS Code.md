# Open Docker Container in VS Code

## Step 1: Install Docker Extension
1. Open **VS Code**.
2. Go to **Extensions** (Ctrl+Shift+X).
3. Search for **Docker** and install the official extension.

## Step 2: Check if Your Container is Running
Run the following command in your terminal:
```bash
docker ps
```
write on terminal:
```bash
code .
```

## Step 3: Attach VS Code to the Running Container
1. Open **VS Code**.
2. Press **Ctrl+Shift+P** to open the command palette.
3. Instead of searching for `"Remote-Containers: Attach to Running Container"`, open **Remote Explorer** and focus on **Dev Containers View** as shown below:
   
![image](https://github.com/user-attachments/assets/4965783b-9129-49d6-8620-105223f82303)

5. Select your container (`shir:3` or the relevant container).

   ![image](https://github.com/user-attachments/assets/9c8fbf6b-f3ff-4605-b880-a3786b195b7f)

## Step 4: Open Your Project Folder
1. In **VS Code**, go to **File > Open Folder**.
2. Navigate to:
   ```
   /workspace/ssl_project
   ```
3. Click **OK** to open the project.

## Step 5: Verify and Work Inside the Container
- Use the integrated terminal in VS Code (**Ctrl+`**) to run commands inside the container.
- If you see the wrong folders, navigate manually in the **Explorer** tab and open `/workspace/ssl_project`.

🚀 Your container is now ready to use in VS Code!

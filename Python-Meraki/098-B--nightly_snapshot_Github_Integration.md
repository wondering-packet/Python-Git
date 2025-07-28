# Setting up a Git repo

### script 098-A is taking nightly snapshots. let's push a copy of the snapshots to a private repo for change history & tracking. this can be useful for compliance as well.

---

1.  **cd into your snapshot folder, e.g.**
    ```bash
    cd /automation/python-data/99-nightly_snapshot
    ```

2.  **initialize git in the directory:**
    ```bash
    git init
    ```

3.  **change default branch to "main"**
    ```bash
    git branch -m main
    ```

4.  **configure username & email. not required if already configured.**
    ```bash
    git config user.name "Your Name"
    ```
    ```bash
    git config --global user.name # validate
    ```
    ```bash
    git config user.email "your.email@example.com"
    ```
    ```bash
    git config user.email # validate
    ```

5.  **goto github & create a new private repo**
    * name it "meraki-snapshot" or whatever you like.

6.  **connect the remote repo**
    ```bash
    git remote add origin [https://github.com/yourusername/meraki-snapshots.git](https://github.com/yourusername/meraki-snapshots.git)
    ```
    ```bash
    git remote -v # validate
    ```

7.  **stage untracked files (you need to have atleasst one snapshot file in your directory)**
    ```bash
    git add .
    ```

8.  **commit**
    ```bash
    git commit -m "first commit"
    ```

9.  **push**
    ```bash
    git push -u origin main
    ```

10. **run script 098-C.**
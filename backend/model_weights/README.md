Put your 3 trained weight files here, named exactly:

- cnn_model.pth
- resnet18_model.pth
- alexnet_model.pth

These files are tracked with **Git LFS** (see `.gitattributes` at the repo root) because
`.pth` files are typically too large for a normal git blob and for GitHub's 100MB hard limit.

Before adding them, run once per clone:

    git lfs install
    git lfs track "*.pth"

Then `git add`, `git commit`, `git push` as normal — LFS handles the rest transparently.

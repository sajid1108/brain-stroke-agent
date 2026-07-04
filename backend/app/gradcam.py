import base64
import io

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image


def generate_gradcam(model, img_tensor, target_layer):
    """Returns the Grad-CAM heatmap, predicted class index, and softmax probabilities."""
    model.eval()
    hooks = {"acts": [], "grads": []}

    fh = target_layer.register_forward_hook(lambda m, i, o: hooks["acts"].append(o))
    bh = target_layer.register_full_backward_hook(lambda m, gi, go: hooks["grads"].append(go[0]))

    output = model(img_tensor)
    probs = F.softmax(output, dim=1)[0]
    pred_class = output.argmax(dim=1).item()

    model.zero_grad()
    output[0, pred_class].backward()
    fh.remove()
    bh.remove()

    act = hooks["acts"][0][0]
    grad = hooks["grads"][0][0]
    weights = grad.mean(dim=(1, 2))

    cam = torch.zeros(act.shape[1:], dtype=torch.float32, device=act.device)
    for i, w in enumerate(weights):
        cam += w * act[i]

    cam = np.maximum(cam.detach().cpu().numpy(), 0)
    cam = cam / cam.max() if cam.max() > 0 else cam
    return cam, pred_class, probs.detach().cpu().numpy()


def overlay_cam_on_image_b64(pil_image: Image.Image, cam: np.ndarray) -> str:
    """Overlays the Grad-CAM heatmap on the original image and returns a base64 PNG string."""
    orig = np.array(pil_image.convert("RGB"))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    heatmap = cv2.resize(heatmap, (orig.shape[1], orig.shape[0]))
    overlay = np.uint8(0.5 * heatmap + 0.5 * orig)

    buf = io.BytesIO()
    Image.fromarray(overlay).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

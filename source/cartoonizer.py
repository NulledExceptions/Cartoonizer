import argparse
import os
import inspect
import socket
import threading
import time
import types
import webbrowser
from pathlib import Path
from typing import Optional

import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import gradio as gr

APP_DIR = Path(__file__).resolve().parent
FAVICON_PATH = APP_DIR / "cartoonizer_web_icon.png"
MAX_IMAGE_SIDE = int(os.environ.get("CARTOONIZER_MAX_SIDE", "768"))


def log(msg: str) -> None:
    print(f"[Cartoonizer] {msg}", flush=True)


CUSTOM_CSS = """
:root {
    --brand-gradient: radial-gradient(circle at 15% 20%, #fcd3a1, #fb8c6a 35%, #482579 85%);
}
.gradio-container {
    font-family: "Inter", "Helvetica Neue", sans-serif;
    background: #0d0d17;
    background-image: radial-gradient(circle at 20% 20%, rgba(255,255,255,0.06), transparent 45%),
                      radial-gradient(circle at 80% 0%, rgba(255,255,255,0.05), transparent 55%);
    color: #f8fafc;
}
.hero-card {
    background: var(--brand-gradient);
    border-radius: 28px;
    padding: 36px 44px;
    color: #111016;
    margin-bottom: 16px;
    box-shadow: 0 20px 60px rgba(16, 5, 50, 0.4);
}
.hero-card h1 {
    font-size: 2.8rem;
    margin-bottom: 0.2rem;
}
.hero-card p {
    font-size: 1.1rem;
    color: rgba(17, 16, 22, 0.8);
}
.hero-card .eyebrow {
    letter-spacing: 0.25em;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}
.stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
}
.stat-card {
    border-radius: 18px;
    padding: 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}
.stat-card span {
    display: block;
    font-size: 2rem;
    font-weight: 700;
    color: #ffd19c;
}
.panel-row {
    gap: 20px;
}
.panel, .output-panel {
    background: rgba(15, 15, 25, 0.85);
    border-radius: 22px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 15px 35px rgba(0,0,0,0.35);
}
.output-panel {
    backdrop-filter: blur(8px);
}
.gradio-container footer,
.gradio-container #footer,
.gradio-container .svelte-1ipelgc,
.gradio-container [class*="built-with"],
.gradio-container a[href*="gradio"],
.gradio-container button[data-testid="api-info-button"],
.gradio-container #api-page {
    display: none !important;
}
.status-box textarea {
    font-family: "JetBrains Mono", "SFMono-Regular", monospace;
    font-size: 0.95rem;
    min-height: 150px;
}
"""


# ---------------------------
# Device / model loading
# ---------------------------

def get_device() -> str:
    """Choose best available device: MPS (Apple), CUDA, or CPU."""
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available() and torch.version.cuda:
        return "cuda"
    return "cpu"


def load_img2img_pipeline(
    model_id: str,
    device: Optional[str] = None,
    use_half: bool = True,
) -> StableDiffusionImg2ImgPipeline:
    """
    Load a Stable Diffusion img2img pipeline.
    model_id: Hugging Face model id, e.g. 'Lykon/dreamshaper-8'.
    """
    if device is None:
        device = get_device()

    # MPS has issues with float16 VAE decoding (produces black images).
    # Use float16 only on CUDA, float32 everywhere else for compatibility.
    if use_half and device == "cuda":
        dtype = torch.float16
    else:
        dtype = torch.float32

    log(f"Loading pipeline '{model_id}' on {device} (dtype={dtype})")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        safety_checker=None,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    )

    try:
        pipe = pipe.to(device)
    except (AssertionError, RuntimeError) as exc:
        log(f"Failed to move pipeline to {device}: {exc}. Falling back to CPU.")
        device = "cpu"
        pipe = pipe.to(device)

    final_device = torch.device(device)
    try:
        object.__setattr__(pipe, "_execution_device", final_device)
    except Exception:
        pass

    original_encode_prompt = pipe.encode_prompt.__func__  # unbound function
    encode_prompt_sig = inspect.signature(original_encode_prompt)

    def _encode_prompt_fixed(self, *args, **kwargs):
        bound = encode_prompt_sig.bind(self, *args, **kwargs)
        bound.arguments["device"] = final_device
        return original_encode_prompt(*bound.args, **bound.kwargs)

    pipe.encode_prompt = types.MethodType(_encode_prompt_fixed, pipe)
    if hasattr(pipe.scheduler, "to"):
        pipe.scheduler = pipe.scheduler.to(final_device)
    if hasattr(pipe.scheduler, "set_timesteps"):
        original_set_timesteps = pipe.scheduler.set_timesteps.__func__
        set_timesteps_sig = inspect.signature(original_set_timesteps)

        def _set_timesteps_fixed(self, *args, **kwargs):
            bound = set_timesteps_sig.bind(self, *args, **kwargs)
            bound.arguments["device"] = final_device
            return original_set_timesteps(*bound.args, **bound.kwargs)

        pipe.scheduler.set_timesteps = types.MethodType(_set_timesteps_fixed, pipe.scheduler)
    original_prepare_latents = pipe.prepare_latents.__func__  # unbound
    prepare_latents_sig = inspect.signature(original_prepare_latents)

    def _prepare_latents_fixed(self, *args, **kwargs):
        bound = prepare_latents_sig.bind(self, *args, **kwargs)
        bound.arguments["device"] = final_device
        bound.arguments["generator"] = bound.arguments.get("generator")
        image = bound.arguments.get("image")
        if image is not None:
            bound.arguments["image"] = image.to(final_device, memory_format=torch.contiguous_format)
        return original_prepare_latents(*bound.args, **bound.kwargs)

    pipe.prepare_latents = types.MethodType(_prepare_latents_fixed, pipe)

    pipe.enable_attention_slicing()
    try:
        pipe.enable_vae_slicing()
        pipe.enable_vae_tiling()
    except Exception:
        pass

    # xFormers is CUDA-only; ignore errors on Mac.
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass

    return pipe


def pick_server_port(preferred: int = 7860) -> int:
    """Return an available TCP port, preferring the provided value."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def prepare_image(path: str, max_side: int = MAX_IMAGE_SIDE) -> Image.Image:
    """
    Load an image and resize while keeping aspect ratio so that
    the largest side is at most max_side.
    """
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = min(max_side / max(w, h), 1.0)
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


# ---------------------------
# Core cartoonization functions
# ---------------------------

def cartoonize_single(
    pipe: StableDiffusionImg2ImgPipeline,
    input_path: str,
    output_path: str,
    style: str = "anime",
    prompt_extra: str = "",
    strength: float = 0.6,
    guidance_scale: float = 7.5,
    steps: int = 30,
    seed: Optional[int] = None,
) -> str:
    """
    Cartoonize one image and save it to output_path.
    """
    presets = {
        "anime": "highly detailed anime style, clean lines, cel shading, vibrant colors",
        "comic": "comic book style, bold ink outlines, halftone shading, dramatic lighting",
        "pixar": "3D Pixar style, soft lighting, smooth shading, expressive eyes",
        "sketch": "clean line art sketch, black ink, minimal shading, white background",
        "watercolor": "soft watercolor painting, pastel colors, gentle edges",
    }

    base = presets.get(style.lower(), presets["anime"])
    prompt = base + (", " + prompt_extra if prompt_extra else "")
    negative_prompt = "blurry, distorted, extra limbs, text, logo, low quality"

    img = prepare_image(input_path)

    generator = None    # type: ignore
    if seed is not None:
        generator = torch.Generator(device=pipe.device).manual_seed(seed)

    result = pipe(
        prompt=prompt,
        image=img,
        strength=strength,
        guidance_scale=guidance_scale,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        generator=generator,
    )
    out_img = result.images[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out_img.save(output_path)
    return output_path


def cartoonize_folder(
    pipe: StableDiffusionImg2ImgPipeline,
    in_dir: str,
    out_dir: str,
    **kwargs,
):
    """
    Cartoonize all supported images in a folder.
    """
    os.makedirs(out_dir, exist_ok=True)
    for fname in os.listdir(in_dir):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
            continue
        input_path = os.path.join(in_dir, fname)
        output_name = os.path.splitext(fname)[0] + "_cartoon.png"
        output_path = os.path.join(out_dir, output_name)
        print(f"[+] {input_path} -> {output_path}")
        cartoonize_single(pipe, input_path, output_path, **kwargs)


# ---------------------------
# Gradio GUI
# ---------------------------

def build_ui(default_model: str = "Lykon/dreamshaper-8"):
    """
    Build the Gradio UI for interactive use.
    """
    device = get_device()
    cache = {"pipe": None, "model": None}

    def ensure_pipe(model_id: str, progress: Optional[gr.Progress] = None):
        if cache["pipe"] is None or cache["model"] != model_id:
            if progress is not None:
                progress(0.0, desc=f"Loading model {model_id}")
            log(f"Initializing pipeline for model '{model_id}'")
            cache["pipe"] = load_img2img_pipeline(model_id, device=device)
            cache["model"] = model_id
            if progress is not None:
                progress(1.0, desc="Model ready")
            log("Pipeline ready")
        return cache["pipe"]

    def infer(
        image: Image.Image,
        style: str,
        extra: str,
        strength: float,
        guidance: float,
        steps: int,
        seed: int,
        model_id: str,
        max_side: int,
        progress: gr.Progress = gr.Progress(track_tqdm=True),
    ):
        if image is None:
            return None, "Please upload an image to begin."

        status_lines = []
        status_lines.append("Loading/initializing model (first run may take several minutes)...")
        log("Starting inference job")
        pipe = ensure_pipe(model_id, progress=progress)
        status_lines.append(f"Model ready on {pipe.device}. Generating image...")

        presets = {
            "Anime": "highly detailed anime style, clean lines, cel shading, vibrant colors",
            "Comic": "comic book style, bold ink outlines, halftone shading, dramatic lighting",
            "Pixar": "3D Pixar style, soft lighting, smooth shading, expressive eyes",
            "Sketch": "clean line art sketch, black ink, minimal shading, white background",
            "Watercolor": "soft watercolor painting, pastel colors, gentle edges",
        }
        base = presets.get(style, presets["Anime"])
        prompt = base + (", " + extra if extra else "")
        negative_prompt = "blurry, distorted, extra limbs, text, logo"

        gen = None   # type: ignore
        if seed >= 0:
            gen = torch.Generator(device=pipe.device).manual_seed(seed)

        # Resize image according to user setting
        img = image.convert("RGB")
        w, h = img.size
        scale = min(max_side / max(w, h), 1.0)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        status_lines.append(f"Processing at resolution {img.size[0]}x{img.size[1]}...")

        result = pipe(
            prompt=prompt,
            image=img,
            strength=strength,
            guidance_scale=guidance,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            generator=gen,
        )
        status_lines.append("Done!")
        return result.images[0], "\n".join(status_lines)

    def update_status_text(status: str) -> str:
        """Pass status strings from the hidden State to the visible textbox."""
        return status

    theme = gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="violet",
        neutral_hue="slate",
    ).set(
        body_background_fill="transparent",
        body_background_fill_dark="transparent",
        block_background_fill="rgba(15,15,25,0.9)",
    )
    favicon = str(FAVICON_PATH) if FAVICON_PATH.exists() else None

    with gr.Blocks(
        title="Cartoonizer Studio",
        theme=theme,
        css=CUSTOM_CSS,
        analytics_enabled=False,
        show_api=False,
        favicon_path=favicon,
    ) as demo:
        gr.HTML(
            """
            <div class="hero-card">
                <div class="eyebrow">LOCAL & PRIVATE</div>
                <h1>Cartoonizer Studio</h1>
                <p>Transform portraits, pets, or product shots into expressive cartoon looks without ever leaving your Mac.</p>
            </div>
            """,
            elem_classes="hero-card",
        )
        gr.HTML(
            """
            <div class="stats-row">
                <div class="stat-card"><span>5</span>Signature styles</div>
                <div class="stat-card"><span>MPS</span>Apple Silicon acceleration</div>
                <div class="stat-card"><span>Offline</span>No cloud uploads</div>
            </div>
            """,
            elem_classes="stats-row",
        )

        with gr.Row(elem_classes="panel-row"):
            with gr.Column(scale=1, elem_classes="panel"):
                img = gr.Image(
                    type="pil",
                    label="Drop an image or click to upload",
                )
                style = gr.Radio(
                    ["Anime", "Comic", "Pixar", "Sketch", "Watercolor"],
                    value="Anime",
                    label="Style palette",
                )
                extra = gr.Textbox(
                    label="Prompt seasoning",
                    placeholder="e.g. neon rim light, painterly shadows",
                )
                strength = gr.Slider(
                    0.1, 1.0, 0.6, step=0.05, label="Strength"
                )
                guidance = gr.Slider(
                    3, 15, 7.5, step=0.5, label="Guidance scale"
                )
                steps = gr.Slider(
                    10, 50, 30, step=1, label="Steps"
                )
                seed = gr.Number(
                    label="Seed (>=0 for reproducible, -1 random)",
                    value=-1,
                    precision=0,
                )
                model_id = gr.Textbox(
                    label="Model ID (Hugging Face)",
                    value=default_model,
                    placeholder="e.g. Lykon/dreamshaper-8",
                )
                max_side = gr.Slider(
                    512, 2048, 768, step=128, label="Max resolution (pixels)"
                )
                btn = gr.Button("Generate", variant="primary")

            with gr.Column(scale=1, elem_classes="output-panel"):
                out = gr.Image(label="Cartoonized Output")
                initial_status = "Idle. Upload an image and click Generate to start."
                status_box = gr.Textbox(
                    label="Status / Progress",
                    value=initial_status,
                    interactive=False,
                    lines=6,
                    elem_classes="status-box",
                )
                status_state = gr.State(initial_status)

        generate_event = btn.click(
            infer,
            [img, style, extra, strength, guidance, steps, seed, model_id, max_side],
            [out, status_state],
        )
        generate_event.then(
            update_status_text,
            inputs=status_state,
            outputs=status_box,
            show_progress=False,
        )
        demo.queue(concurrency_count=1, max_size=8)

    return demo


# ---------------------------
# CLI
# ---------------------------

def parse_args():
    ap = argparse.ArgumentParser(
        description="Local photo-to-cartoon converter using Stable Diffusion img2img."
    )
    ap.add_argument(
        "--model",
        default="Lykon/dreamshaper-8",
        help="Hugging Face model id (SD 1.5-based).",
    )
    ap.add_argument(
        "--style",
        default="anime",
        help="Style preset: anime, comic, pixar, sketch, watercolor.",
    )
    ap.add_argument(
        "--prompt-extra",
        default="",
        help="Extra prompt text to append (optional).",
    )
    ap.add_argument(
        "--strength",
        type=float,
        default=0.6,
        help="How much to change the image (0.1–1.0).",
    )
    ap.add_argument(
        "--guidance-scale",
        type=float,
        default=7.5,
        help="Style intensity.",
    )
    ap.add_argument(
        "--steps",
        type=int,
        default=30,
        help="Number of inference steps.",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=-1,
        help="Random seed (>=0 for reproducible results, -1 for random).",
    )
    ap.add_argument(
        "--input",
        help="Input image path (single-image mode).",
    )
    ap.add_argument(
        "--output",
        help="Output image path (single-image mode).",
    )
    ap.add_argument(
        "--input-folder",
        help="Input folder (batch mode).",
    )
    ap.add_argument(
        "--output-folder",
        default="cartoon_out",
        help="Output folder (batch mode).",
    )
    ap.add_argument(
        "--gui",
        action="store_true",
        help="Launch Gradio web UI instead of CLI.",
    )
    return ap.parse_args()


def main():
    args = parse_args()

    # GUI mode (used by the .app launcher)
    if args.gui:
        demo = build_ui(default_model=args.model)
        port = pick_server_port(7860)
        if port != 7860:
            print(f"[i] Port 7860 unavailable, using {port} instead.")
        url = f"http://127.0.0.1:{port}"
        log(f"Starting Cartoonizer GUI at {url}")

        def _auto_open():
            time.sleep(2)
            try:
                webbrowser.open(url, new=1, autoraise=True)
            except Exception as exc:
                print(f"[w] Could not open browser automatically: {exc}")

        threading.Thread(target=_auto_open, daemon=True).start()
        demo.launch(
            server_name="127.0.0.1",
            server_port=port,
            share=False,
            inbrowser=False,
        )
        return

    # CLI mode
    if not args.input and not args.input_folder:
        print("Provide --input or --input-folder (or use --gui for the UI).")
        return

    device = get_device()
    print(f"[i] Using device: {device}")
    print(f"[i] Loading model: {args.model}")
    pipe = load_img2img_pipeline(args.model, device=device)

    kwargs = dict(
        style=args.style,
        prompt_extra=args.prompt_extra,
        strength=args.strength,
        guidance_scale=args.guidance_scale,
        steps=args.steps,
        seed=args.seed if args.seed >= 0 else None,
    )

    if args.input:
        output_path = args.output
        if not output_path:
            root, _ = os.path.splitext(args.input)
            output_path = root + "_cartoon.png"
        print(f"[+] Cartoonizing {args.input} -> {output_path}")
        cartoonize_single(pipe, args.input, output_path, **kwargs)

    if args.input_folder:
        print(f"[+] Cartoonizing folder {args.input_folder} -> {args.output_folder}")
        cartoonize_folder(pipe, args.input_folder, args.output_folder, **kwargs)


if __name__ == "__main__":
    main()

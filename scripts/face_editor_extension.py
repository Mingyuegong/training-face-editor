import gradio as gr
import modules.scripts as scripts

from scripts import face_editor


class FaceEditorExtension(scripts.Script):
    def __init__(self) -> None:
        super().__init__()
        self.__is_running = False

    def title(self):
        return "Face Editor EX"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("Face Editor", open=False, elem_id="sd-face-editor-extension"):
            script = face_editor.Script()
            enabled = gr.Checkbox(label="Enabled", value=False)
            components = [enabled] + script.ui(is_img2img)
            self.infotext_fields = [(enabled, script.add_prefix("enabled"))] + script.components
            return components

    def before_process_batch(self, p, enabled: bool,
                             face_margin: float,
                             confidence: float,
                             strength1: float,
                             strength2: float,
                             max_face_count: int,
                             mask_size: int,
                             mask_blur: int,
                             prompt_for_face: str,
                             apply_inside_mask_only: bool,
                             save_original_image: bool,
                             show_intermediate_steps: bool,
                             apply_scripts_to_faces: bool,
                             face_size: int,
                             use_minimal_area: bool,
                             ignore_larger_faces: bool,
                             **kwargs):
        if not enabled or self.__is_running:
            return
        if not save_original_image:
            p.do_not_save_samples = True

        if p.scripts is not None and hasattr(p.scripts, 'alwayson_scripts') and p.scripts.alwayson_scripts[-1] != self:
            for i, e in enumerate(p.scripts.alwayson_scripts):
                if e == self:
                    p.scripts.alwayson_scripts.append(p.scripts.alwayson_scripts.pop(i))
                    break

    def postprocess(self, o, res,
                    enabled: bool,
                    face_margin: float,
                    confidence: float,
                    strength1: float,
                    strength2: float,
                    max_face_count: int,
                    mask_size: int,
                    mask_blur: int,
                    prompt_for_face: str,
                    apply_inside_mask_only: bool,
                    save_original_image: bool,
                    show_intermediate_steps: bool,
                    apply_scripts_to_faces: bool,
                    face_size: int,
                    use_minimal_area: bool,
                    ignore_larger_faces: bool):
        if not enabled or self.__is_running:
            return

        if isinstance(enabled, dict):
            face_margin = enabled.get("face_margin", face_margin)
            confidence = enabled.get("confidence", confidence)
            strength1 = enabled.get("strength1", strength1)
            strength2 = enabled.get("strength2", strength2)
            max_face_count = enabled.get("max_face_count", max_face_count)
            mask_size = enabled.get("mask_size", mask_size)
            mask_blur = enabled.get("mask_blur", mask_blur)
            prompt_for_face = enabled.get("prompt_for_face", prompt_for_face)
            apply_inside_mask_only = enabled.get("apply_inside_mask_only", apply_inside_mask_only)
            save_original_image = enabled.get("save_original_image", save_original_image)
            show_intermediate_steps = enabled.get("show_intermediate_steps", show_intermediate_steps)
            apply_scripts_to_faces = enabled.get("apply_scripts_to_faces", apply_scripts_to_faces)
            face_size = enabled.get("face_size", face_size)
            use_minimal_area = enabled.get("use_minimal_area", use_minimal_area)
            ignore_larger_faces = enabled.get("ignore_larger_faces", ignore_larger_faces)

        try:
            self.__is_running = True

            o.do_not_save_samples = False
            script = face_editor.Script()
            mask_model, detection_model = script.get_face_models()

            script.proc_images(mask_model, detection_model, o, res,
                               face_margin=face_margin, confidence=confidence,
                               strength1=strength1, strength2=strength2,
                               max_face_count=max_face_count, mask_size=mask_size,
                               mask_blur=mask_blur, prompt_for_face=prompt_for_face,
                               apply_inside_mask_only=apply_inside_mask_only,
                               show_intermediate_steps=show_intermediate_steps,
                               apply_scripts_to_faces=apply_scripts_to_faces,
                               face_size=face_size,
                               use_minimal_area=use_minimal_area,
                               ignore_larger_faces=ignore_larger_faces)

        finally:
            self.__is_running = False

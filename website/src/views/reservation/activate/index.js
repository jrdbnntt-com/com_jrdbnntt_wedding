import "website/src/views/_templates/main/index"
import "./index.scss"
import * as $ from "jquery";
import {attach} from "website/src/js/recaptcha";

// Attach recaptcha to submit button
$(document).ready(() => {
    let $form = $('#form_activate');
    let $hiddenRecaptchaTokenInput = $form.find('input[name="recaptcha_token"]');
    try {
        attach($form, $hiddenRecaptchaTokenInput);
    } catch (err) {
        console.error("failed to attach recaptcha to submit button:", err);
    }
});

let statusId;
let startSlider;
let endSlider;
let startLabel;
let endLabel;

export function timeSliderHandler(ids) {
    startSlider = document.getElementById(ids.startSliderId);
    endSlider = document.getElementById(ids.endSliderId);
    startLabel = document.getElementById(ids.startLabelId);
    endLabel = document.getElementById(ids.endLabelId);
}

//is_edit
var is_edit = document.getElementById("is_edit").value;

//-----------  Calculate age by dob---------------//
// 1. declear variables
var dob = document.getElementById("id_dob");
var ageResult = document.getElementById("ageResult");
var ageLabel = document.querySelector('label[for="ageResult"]');

// Initialize age calculation when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Calculate age on page load if DOB already has a value
    // This handles both edit mode and when form reloads after server validation failure
    if (dob && dob.value) {
        calculateAge(dob.value);
    }
    
    // If form was submitted but failed validation, show appropriate messages
    const formAction = document.getElementById('form-action');
    
    if (formAction && formAction.value === 'submited') {
        // Form was submitted but validation failed
        // Make sure age is calculated
        if (dob && dob.value) {
            calculateAge(dob.value);
        }
        
        // Check if photo is missing after form submission failure
        const photoInput = document.getElementById('id_photo');
        const isEditMode = is_edit === 'edit';
        const currentPhotoDisplay = document.querySelector('.current-photo-display');
        const capturedPhotoBlob = window.capturedPhotoBlob;
        const photoPreview = document.getElementById('photo-preview');
        const cameraPhotoPreview = document.getElementById('camera-photo-preview');

        // Check if photo exists through any means
        const hasFileUpload = photoInput && photoInput.files && photoInput.files.length > 0;
        const hasCapturedPhoto = capturedPhotoBlob;
        const hasPhotoPreview = photoPreview && photoPreview.style.display !== 'none';
        const hasCameraPreview = cameraPhotoPreview && cameraPhotoPreview.style.display !== 'none';
        const hasCurrentPhoto = currentPhotoDisplay;

        if (!isEditMode && photoInput && !hasFileUpload && !hasCapturedPhoto && !hasPhotoPreview && !hasCameraPreview && !hasCurrentPhoto) {
            // Only show this message if we're in create mode and absolutely no photo exists
            if (typeof toast !== 'undefined') {
                toast.info('Please upload or capture a worker photo to continue');
            }
            // Focus on the photo field to guide the user
            const photoSection = photoInput.closest('.col-span-1');
            if (photoSection) {
                photoSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }
});

// Also handle page fully loaded
window.addEventListener('load', function() {
    // Ensure age is calculated even if DOM ready fired too early
    if (dob && dob.value && (!ageResult || !ageResult.value)) {
        calculateAge(dob.value);
    }
});

// 2. triger dob input date
if (dob) {
    dob.addEventListener("change", (e)=>calculateAge(e.target.value));
}
// 3. create function for calculate age by dob
function calculateAge(dob){
    if (!dob || !ageResult) {
        return;
    }
    
    //declar var
    const birthDate = new Date(dob);
    const today = new Date();

    //start calculate
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    const dayDiff = today.getDate() - birthDate.getDate()
      // Adjust age if the birthday hasn't occurred yet this year
    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
        age--;
    }
    
    //set value to input
    ageResult.value = age;
    
    //check age allowed
    const ageIsAllowed = checkAgeAllow(age);
    
    if(!ageIsAllowed){
        toggleCssClass(ageResult, ["text-red-500" ],"add")
        toggleCssClass(ageLabel, ["text-red-500"], "add")
    }else{
        toggleCssClass(ageResult, ["text-red-500" ],"remove")
        toggleCssClass(ageLabel, ["text-red-500"], "remove")
    }

}

// create function to check age allow
function checkAgeAllow(age){
    if (age >=16){
        return true;
    }
    return false;
}

//------------validate phone number formate --------------//
// 1. declear variables
var phoneNumber = document.getElementById("id_phone_number");
var phoneNumberLabel = document.querySelector('label[for="id_phone_number"]');
// 2. triger phone number input - only format if provided, no validation
if (phoneNumber) {
    phoneNumber.addEventListener("change", (e)=>{
        if(e.target.value && e.target.value.trim() !== '') {
            formatPhoneNumber(e.target.value);
        }
    });
}

// 3. create function to format phone number (optional field, no validation)
function formatPhoneNumber(phone){
    if (!phone || phone.trim() === '') {
        return; // Phone number is optional, skip if empty
    }

    //declare result
    let result = phone;
    // Remove non-digit characters
    let digits = phone.replace(/\D/g, '');

    // Only format if it looks like a Cambodian number
    if (digits.length >= 8) {
        // Convert leading '0' to '+855' if needed
        if (digits.startsWith('0')) {
            digits = '855' + digits.slice(1);
        }

        // Format if it starts with 855
        if (digits.startsWith('855') && digits.length >= 11) {
            const prefix = digits.slice(3, 5);
            const middle = digits.slice(5, 8);
            const last = digits.slice(8);

            result = `+855 ${prefix} ${middle} ${last}`;
        }
    }

    // Always clear error styling since phone is optional
    if (phoneNumber) {
        toggleCssClass(phoneNumber,["text-red-500"], "remove");
    }
    if (phoneNumberLabel) {
        toggleCssClass(phoneNumberLabel,["text-red-500"], "remove");
    }

    if (phoneNumber) {
        phoneNumber.value = result;
    }
}


//------- worker information ------------------//
//1. declaer var
var zon = document.getElementById("id_zone");
var building = document.getElementById("id_building");
var floor = document.getElementById("id_floor");

// Get worker data from the template
let workerData = null;
try {
    const workerDataScript = document.getElementById('worker-data');
    if (workerDataScript) {
        workerData = JSON.parse(workerDataScript.textContent);
    }
} catch (e) {
}

//2. disabled select on window load and trigger select
window.addEventListener('DOMContentLoaded', function(){

    if(!is_edit){
        toggleAttr(building,"disabled","add");
        toggleAttr(floor, "disabled", "add")
        toggleAttr(floor, "disabled", "add")
        toggleAttr(floor, "disabled", "add")

    } else if (workerData && workerData.is_edit === 'edit') {
        // In edit mode, populate the dropdowns with worker's current values
        if (workerData.worker_zone_id) {
            zon.value = workerData.worker_zone_id;
            onUpdateBuilding(workerData.worker_zone_id);
        }
    }

});

// on zon trigger
zon.addEventListener('change', (e)=>onUpdateBuilding(e.target.value))
// on building trigger
building.addEventListener('change', (e)=>onUpdateFloor(e.target.value))

//3. create functio for trigger
function onUpdateBuilding(zoneId){
   
    // Use AJAX to get fresh building data to ensure consistency
    fetch('/zone/ajax/get-buildings-by-zone/?zone_id=' + zoneId)
    .then(response => response.json())
    .then(data => {

        building.innerHTML = '<option value="">Select Building</option>';
        
        if (data.buildings && data.buildings.length > 0) {

            data.buildings.forEach(build => {
                const option = document.createElement('option');
                option.value = build.id;
                option.textContent = build.name;
                if (workerData && workerData.worker_building_id && build.id.toString() === workerData.worker_building_id.toString()) {
                    option.selected = true;
                    onUpdateFloor(build.id);
                }
                building.appendChild(option);
            });

            toggleAttr(building, "disabled", "remove")

            

        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No buildings available for this zone';
            option.disabled = true;
            building.appendChild(option);
            toggleAttr(building, "disabled", "add")
            toggleAttr(floor, "disabled", "add")
        }
    })
    .catch(error => {
        // Error fetching buildings - using fallback
        // Fallback to static data if AJAX fails
       
    });

}

function onUpdateFloor(buildingId){

    floor.innerHTML = '<option value="">Loading floors...</option>';

    fetch('/zone/ajax/get-floors-by-building/?building_id='+buildingId)
    .then(response => response.json())
    .then(data => {

        floor.innerHTML = '<option value="">Select Floor</option>';

        if (data.floors && data.floors.length > 0) {

            data.floors.forEach(flr => {
                const option = document.createElement('option');
                option.value = flr.id;
                option.textContent = flr.name;
                if (workerData && workerData.worker_floor_id && flr.id.toString() === workerData.worker_floor_id.toString()) {
                    option.selected = true;
                }

                floor.appendChild(option);
            });

            toggleAttr(floor, "disabled", "remove")

        } else {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No floors available for this building';
            option.disabled = true;
            floor.appendChild(option);
            floor.disabled = true;
           
        }
    })
    .catch(error => {
        // Error fetching floors - using fallback
        floor.innerHTML = '<option value="">Error loading floors</option>';
        floor.disabled = true;
    });
}




//disable 
function displayUploadImagePreview(e){

    if(isScanning == false){
        //set loading
	extractLoading.style.display = "block";
    toggleCssClass(textLoading, ["hidden"], "remove")

    let file = e.target.files[0];
    const formData = new FormData();
    formData.append('image', file);
    let url = window.URL.createObjectURL(file);
    documentImage.src= url;
    documentImage.style.display = "block";
    documentImageIcon.style.display="none";

    //call passport OCR API to extract data
    fetch('/zone/workers/ocr/image/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // image doc
        documentImage.src = url;
        documentImageIcon.style.display = "none";
        documentImage.style.display = "block";

        //set loading
        extractLoading.style.display = "none";
        toggleCssClass(textLoading, ["hidden"], "add")

        //doc no
        docNo.value = data.data[12].toString();

        //doc type
        docType.value = data.data[25].toString().toLowerCase();

        //issue authority
        docIssueAuthority.value = data.data[4].toString();

        //issues date
        docIssueDate.value = formatToMMDDYYYY(data.data[17].toString());
        // issueDateError.innerHTML = formatToMMDDYYYY(data.data[17].toString());

        //expired date
        docExpiryDate.value = formatToMMDDYYYY(data.data[19].toString());
        // expiryDateLabelError.innerHTML = formatToMMDDYYYY(data.data[19].toString());
        //check expiry date
        var expiryDate = new Date(docExpiryDate.value);
        var today = new Date();
        if(expiryDate < today){

            docExpiryDate.value =null;
            docExpiryDate.style.color = "red";
            docExpiryDate.style.fontWeight = "bold";
            docExpiryDate.style.border = "1px solid red";
            docExpiryDate.style.textAlign = "left";
            expiryDateLabelError.innerHTML = " ( Expiry date is expired ) ";
            expiredDateError.classList.remove("hidden");
            btnCreateWorker.setAttribute("disabled", "disabled");
            btnCreateWorker.classList.add("disabled");
            return;
        }else{
            docExpiryDate.value = text["Date of Expiry"];
            expiryDateLabelError.innerHTML = "";
            expiredDateError.classList.add("hidden");
            btnCreateWorker.setAttribute("disabled");
            btnCreateWorker.classList.remove("disabled");
        }

        

    })
    .catch(error => {
        //set loading
        extractLoading.style.display = "none";
    });

    return;

    }
    
    let file = e.target.files[0];
    let url = window.URL.createObjectURL(file);
    documentImage.src= url;
    documentImage.style.display = "block";
    documentImageIcon.style.display="none";
}



//create dynamic css classes 
function toggleCssClass(elm, className, option){
    if(option==="add"){
        return elm.classList.add(...className);
    }else{
        return elm.classList.remove(...className);
    }
    
}

//create dynamic css classes 
function toggleCssStyle(elm, style){
   return elm.style=style;
}
//create dynamic attribute
function toggleAttr(elm, attr, option){
    if(option ==="add"){
        return elm.setAttribute(attr,attr)
    }else{
        return elm.removeAttribute(attr)
    }
}


//-------------window onload-----------------//
addEventListener('DOMContentLoaded', function(){
     if(is_edit && is_edit== 'edit'){
     
        let age = dob.value;
        calculateAge(age)       
    }

})
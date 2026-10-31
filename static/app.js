const photoInput=document.getElementById('photo');
if(photoInput){photoInput.addEventListener('change',e=>{const f=e.target.files[0],img=document.getElementById('preview');if(!f)return;img.src=URL.createObjectURL(f);img.hidden=false;});}
function copyText(value){navigator.clipboard.writeText(value).then(()=>{const n=document.createElement('div');n.className='copy-toast';n.textContent='Copied to clipboard';document.body.appendChild(n);setTimeout(()=>n.remove(),1800);}).catch(()=>alert('Copy unavailable in this browser.'));}

function getMyLocation() {
    const message = document.getElementById("location-message");

    if (!navigator.geolocation) {
        message.textContent = "Geolocation is not supported.";
        return;
    }

    message.textContent = "Detecting your location...";

    navigator.geolocation.getCurrentPosition(
        function(position) {
            document.getElementById("latitude").value =
                position.coords.latitude;

            document.getElementById("longitude").value =
                position.coords.longitude;

            const locationInput = document.getElementById("location");

            if (locationInput && !locationInput.value.trim()) {
                locationInput.value =
                `Coordinates: ${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`;
            }
            message.textContent = "Location detected successfully."; 
        },
        function(error) {
            message.textContent =
                "Unable to get location. Please enter coordinates manually.";
        },
        {
            enableHighAccuracy: true,
            timeout: 10000
        }
    );
}

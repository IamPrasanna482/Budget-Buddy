const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector('.invalid-feedback');
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailSuccessOutput = document.querySelector(".emailSuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordField = document.querySelector('#passwordField');
const submitBtn = document.querySelector('.submit-btn');

const handleToggleInput = (e)=>{
    if (showPasswordToggle.textContent === 'SHOW'){
        showPasswordToggle.textContent = 'HIDE';
        passwordField.setAttribute("type","text");
    }
    else{
        showPasswordToggle.textContent = 'SHOW';
        passwordField.setAttribute("type","password");
    }

}

showPasswordToggle.addEventListener('click',handleToggleInput);

emailField.addEventListener('keyup',(e)=>{
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display='none';

    emailSuccessOutput.style.display = 'block';


    emailSuccessOutput.textContent = `Checking ${emailVal}`;

    if(emailVal.length > 0){
// make api call to server using built in fetch function in js
    fetch("/authentication/validate-email",{
        body: JSON.stringify({email:emailVal}),
        method:"POST",
    })
    .then((res)=>res.json())
    .then((data)=>{
        console.log("data",data);
        emailSuccessOutput.style.display = 'none';
        if(data.email_error){
            submitBtn.disabled = true;
            emailField.classList.add("is-invalid");
            emailFeedBackArea.style.display='block';
            emailFeedBackArea.style.margin='10px';
            // feedBackArea.style.font_weight='bold';
            emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`
        }
        else{
            submitBtn.removeAttribute('disabled');
        }
    });
    }
})


usernameField.addEventListener('keyup',(e)=>{
    console.log("testing typing");
    const userNameVal = e.target.value;

    usernameSuccessOutput.style.display = 'block';


    usernameSuccessOutput.textContent = `Checking ${userNameVal}`;

    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display='none';


    if(userNameVal.length > 0){
    fetch("/authentication/validate-username",{   // make api call to server using built in fetch function in js
        body: JSON.stringify({username:userNameVal}),
        method:"POST",
    })
    .then((res)=>res.json())
    .then((data)=>{
        // console.log("data",data);
        usernameSuccessOutput.style.display = 'none';

        if(data.username_error){
            usernameField.classList.add("is-invalid");
            feedBackArea.style.display='block';
            feedBackArea.style.margin='10px';
            // feedBackArea.style.font_weight='bold';
            feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
            submitBtn.disabled = true ;
        }
        else{
            submitBtn.removeAttribute('disabled');
        }
        
    });
    }
});
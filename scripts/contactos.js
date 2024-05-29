// alert ("Hola Mundo")

function validar(){
    var nomape = document.getElementById("full-name")
    var mail = document.getElementById("email-address")
    var phone = document.getElementById("phone")
    var tema = document.querySelector('input[name="tema"]:checked')
    var msg = document.getElementById("message")

    var myModal = new bootstrap.Modal(document.getElementById('staticBackdrop'), { keyboard: false })
   
    if(nomape.value !== "" && mail.value !== ""  && (tema !== null && tema.value > 0) && msg.value !== "" && phone.value !==""){
        if(validarEmail(mail.value) && validarPhone(phone.value)){
            var frm = document.getElementById("fs-frm")
             frm.submit()
            //alert('Enviado')
        }else{
            var errtext = document.getElementById("error-form")
            errtext.innerHTML = (!validarEmail(mail.value) ? "<br>Correo Electrónico" : "") + 
                                (!validarPhone(phone.value) ? "<br>Teléfono" : "")
            
            myModal.toggle()
            mail.focus()
        }
    }else{
        var errtext = document.getElementById("error-form")
        //   Uso de asignación con operador ternario
        errtext.innerHTML= 
            (nomape.value === "" ? "<br>Nombre y Apellido" : "") + 
            (mail.value === "" ? "<br>Correo Electrónico" : "") + 
            (phone.value === "" ? "<br>Teléfono" : "") + 
            (tema === null || tema.value < 1 ? "<br>Tema" : "") + 
            (msg.value === "" ? "<br>Mensaje" : "")
        myModal.toggle()
    }
}

function validarEmail(email){
    return email.toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
}
function validarPhone(phone){
    return phone
    .match(
        /(?:([+]\d{1,4})[-.\s]?)?(?:[(](\d{1,3})[)][-.\s]?)?(\d{1,4})[-.\s]?(\d{1,4})[-.\s]?(\d{1,9})/g
    );
}

function att_formFiltro(operacao) {
    document.getElementById("id_operacao").value = operacao
}

function att_formValidarCertificado(operacao) {
    document.getElementById("id_operacao").value = operacao
}

function fechar_modal_mensagem() {
    document.getElementById("modal_menssagem").style.display = "none";
}

function dropdown() {
    document.getElementById("dropdown-content").style.display = "block";
}

function deletar_certificado() {
    var result = confirm("Esta é uma ação irreversível, deseja mesmo deletar o certificado?")
    if(result == true) {
        att_formValidarCertificado('deletar')
        document.getElementById('form-certificado').submit();
    }
}

function recusar_certificado() {
    var obs = prompt("Qual a justifica? (visível para o aluno)")
    if (obs != null && obs.trim().length > 0 ) {
	document.getElementById("id_observacao").value = obs
        att_formValidarCertificado('recusar')
        document.getElementById('form-certificado').submit();
    }
}

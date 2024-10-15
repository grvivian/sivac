document.getElementById("barra_pesquisa").addEventListener("input", atualizar_certificados);

function atualizar_certificados() {
    $(".elementos_tabela").each(function(i, obj) {
	var x = document.getElementById("barra_pesquisa");
        var nome = document.getElementById(`titulo_${obj.id}`);

        if (x.value == "" || eval(`nome.innerHTML.match(/^${x.value}.*$/i)`)) {
            document.getElementById(obj.id).style.display = "table-row";
        } else {
            document.getElementById(obj.id).style.display = "none";
        }
    });
}

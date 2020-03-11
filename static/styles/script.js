function deleteConfirm() {
  if (confirm("Are you sure you want to delete the recipe?")) {
    document.getElementById("deleteRecipe").value = "1";
    formSubmit.submit();
  }
  else {
    document.getElementById("deleteRecipe").value = "0";
  }
}
function duplicateIngredients() {
  var itm = document.getElementById("ingredients");
  var cln = itm.cloneNode(true);
  cln.querySelector('#ingredientAmount').value = '';
  cln.querySelector('#ingredientUnit').value = 'none';
  cln.querySelector('#ingredientName').value = '';
  document.getElementById("ingredientBox").appendChild(cln);

}
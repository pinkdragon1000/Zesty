function deleteConfirm() {
  if (confirm("Are you sure you want to delete the recipe {{recipeName|safe}}?")) {
    document.getElementById("deleteRecipe").value = "1";
    addEditRecipeForm.submit();
  }
  else {
    document.getElementById("deleteRecipe").value = "0";
  }
}
function duplicateIngredients() {
  //document.getElementByName("ingredientName").value="";
  //document.getElementByName("ingredientAmount").value="";
  //document.getElementByName("ingredientUnit").value="";
  var itm = document.getElementById("ingredients");
  var cln = itm.cloneNode(true);
  cln.querySelector('#ingredientAmount').value = '';
  cln.querySelector('#ingredientUnit').value = 'none';
  cln.querySelector('#ingredientName').value = '';
  document.getElementById("ingredientBox").appendChild(cln);

}
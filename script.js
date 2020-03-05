function deleteConfirm() {
    if (confirm("Are you sure you want to delete the recipe {{recipeName|safe}}?")) {
      document.getElementById("deleteRecipe").value = "1";
      addEditRecipeForm.submit();
      //console.log(document.getElementById("deleteRecipe").value);
    }
    else {
      document.getElementById("deleteRecipe").value = "0";
      //console.log(document.getElementById("deleteRecipe").value);
    }
  }
  function duplicateIngredients() {
    var itm = document.getElementById("ingredients");
    var cln = itm.cloneNode(true);
    document.getElementById("ingredientBox").appendChild(cln);

  }
CREATE TABLE `Users` (
  `userID` int(11) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(128) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` varchar(128) NOT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
);

CREATE TABLE `RecipeInfo` (
  `recipeID` int(11) NOT NULL AUTO_INCREMENT,
  `recipeName` varchar(64) NOT NULL,
  `recipeDescription` varchar(128) DEFAULT NULL,
  `recipeTag` varchar(255) DEFAULT NULL,
  `preparationTime` varchar(128) DEFAULT NULL,
  `yield` varchar(128) DEFAULT NULL,
  `methods` mediumtext,
  `recipeImage` varchar(255) DEFAULT NULL,
  `userID` int(11) DEFAULT NULL,
  `ispublic` tinyint(1) NOT NULL,
  PRIMARY KEY (`recipeID`),
  KEY `fk_userID` (`userID`),
  CONSTRAINT `fk_userID` FOREIGN KEY (`userID`) REFERENCES `Users` (`userID`)
);

CREATE TABLE `RecipeIngredients` (
  `ingredientID` int(11) NOT NULL AUTO_INCREMENT,
  `recipeID` int(11) NOT NULL,
  `ingredientDescription` varchar(128) DEFAULT NULL,
  `ingredientAmount` varchar(255) DEFAULT NULL,
  `ingredientUnit` varchar(128) NOT NULL,
  PRIMARY KEY (`ingredientID`),
  KEY `fk_recipeID` (`recipeID`),
  CONSTRAINT `fk_recipeID` FOREIGN KEY (`recipeID`) REFERENCES `RecipeInfo` (`recipeID`) ON DELETE CASCADE
);

CREATE TABLE `GroceryList` (
  `listID` int(11) NOT NULL AUTO_INCREMENT,
  `recipeID` int(11) NOT NULL,
  `userID` int(11) NOT NULL,
  PRIMARY KEY (`listID`),
  UNIQUE KEY `userID` (`userID`,`recipeID`),
  KEY `fk_userID2` (`userID`),
  KEY `fk_recipeID2` (`recipeID`),
  CONSTRAINT `fk_recipeID2` FOREIGN KEY (`recipeID`) REFERENCES `RecipeInfo` (`recipeID`) ON DELETE CASCADE,
  CONSTRAINT `fk_userID2` FOREIGN KEY (`userID`) REFERENCES `Users` (`userID`) ON DELETE CASCADE
);

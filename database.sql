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
  `userID` int(11) NOT NULL,
  `ispublic` tinyint(1) NOT NULL,
  `ingredients` varchar(2000) NOT NULL, 
  PRIMARY KEY (`recipeID`),
  KEY `fk_userID` (`userID`),
  CONSTRAINT `fk_userID` FOREIGN KEY (`userID`) REFERENCES `Users` (`userID`)
);
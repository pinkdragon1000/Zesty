CREATE TABLE `Users` (
  `userID` int(11) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(128) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` varchar(128) NOT NULL,
  PRIMARY KEY (`userID`),
  UNIQUE KEY `email` (`email`)
);

CREATE TABLE `RecipeInfo`(
 `recipeID` int NOT NULL AUTO_INCREMENT, 
 `recipeName` varchar(64) NOT NULL,
 `recipeDescription` varchar(128),
 `recipeImage` LONGBLOB,
 `userID` int(11),
 PRIMARY KEY (`recipeID`),
 CONSTRAINT `fk_userID`
    FOREIGN KEY (userID) 
        REFERENCES Users(userID)
);

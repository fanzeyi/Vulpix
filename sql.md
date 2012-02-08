
# Database Design

## User

```
CREATE TABLE IF NOT EXISTS `User` (
    `id` INT AUTO_INCREMENT PRIMARY KEY, 
    `Username` VARCHAR(100) CHARACTER SET 'utf-8', 
    `Auth` VARCHAR(200) CHARACTER SET 'utf-8', 
    `E-mail` VARCHAR(200) CHARACTER SET 'utf-8', 
    `Nickname` VARCHAR(200) CHARACTER SET 'utf-8', 
    CHARACTER SET = 'utf-8'
)
```

```
CREATE TABLE IF NOT EXISTS `Problem` (
    `id` INT AUTO_INCREMENT PRIMARY KEY, 
    `Title` TINYTEXT, 
    `Content` LONGTEXT, 
    CHARACTER SET = 'utf-8'
)
```

```
CREATE TABLE IF NOT EXISTS `Diary` (
    `id` INT AUTO_INCREMENT PRIMARY KEY, 
    `Title` TINYTEXT, 
    `Content` LONGTEXT, 
    `pid` INT, 
    CHARACTER SET = 'utf-8'
)
```

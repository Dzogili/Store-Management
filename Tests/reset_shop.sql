DELETE FROM orderproduct;
DELETE FROM productcategory;
DELETE FROM category;
DELETE FROM product;
DELETE FROM order;
ALTER TABLE category AUTO_INCREMENT = 1;
ALTER TABLE order AUTO_INCREMENT = 1;
ALTER TABLE product AUTO_INCREMENT = 1;
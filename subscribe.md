---
layout: post
title: subscribe
---
Please enter your email and click "Submit" to finish. 


<style> 
input[type=button], input[type=submit]{
  background-color: #04AA6D;
  border: none;
  color: white;
  padding: 16px 32px;
  text-decoration: none;
  margin: 4px 2px;
  cursor: pointer;
  
}

input[type=email] {
  border: normal;
  padding: 12px 20px;
  margin: 8px 0;
  box-sizing: border-box;
  margin: 4px 2px;
}

</style>

<form action="/thank-you">
  <label for="email">Enter your email:</label>
  <input type="email" id="email" name="email">
  <input type="submit">
</form>

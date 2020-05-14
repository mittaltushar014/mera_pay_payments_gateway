Website for making payments.    

####Features
Individuals and businesses can signup and login.    
Individuals can shop and make payments via different methods, see their payment history, export their payments history and see the visuals for their payments.  
Businesses can add services, see their payment history, export their payments history and see the visuals for their payments.   
        
####How to run:      
1. Install python3  

2. In terminal, run:    
   -> python3 -m pip install -r requirements.txt    
   -> python3 manage.py makemigrations  
   -> python3 manage.py migrate

3. In settings.py in payments folder write your email and password from which you want to send otp for user verification.
EMAIL_HOST_USER = '--your--email--'
EMAIL_HOST_PASSWORD = '--your--password--'        
   
   -> python3 manage.py runserver       

4. Go to the localhost/log, in browser and start surfing the website.   

5. Select business account or Customer account.
            
 
    

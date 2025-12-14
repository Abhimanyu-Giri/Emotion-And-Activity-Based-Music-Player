
import random

youtube_songs = {
    "positive": [
        "https://www.youtube.com/watch?v=pAxRKgmiTSU", #one piece
        "https://www.youtube.com/watch?v=9bZkp7q19f0" ,  # gaganam
       "https://www.youtube.com/watch?v=2gcsgfzqN8k" ,#zingat
        "https://www.youtube.com/watch?v=rRpfAHwtveQ&ab_channel=VideoPalace" , #zindagi
         "https://www.youtube.com/watch?v=fe9udc210tM&ab_channel=ChillPind" , #with you 
         "https://www.youtube.com/watch?v=9a4izd3Rvdw&ab_channel=YRF" , # challa 
         
         "https://www.youtube.com/watch?v=SuqAsE2NgIQ&ab_channel=YRFMusic"  , #jukebox playlist
         
         
        
    ],
    "neutral": [
        "https://www.youtube.com/watch?v=dx4Teh-nv3A" ,  #namo namo 
        "https://www.youtube.com/watch?v=NFsEqOBG51M" , # aaj se teri
        "https://www.youtube.com/watch?v=FupW3gNXowI&ab_channel=EverestMarathi" , #ka kalena
         "https://www.youtube.com/watch?v=d6KJkavA8zk&ab_channel=SonyMusicIndia" , # ja ne tu
        "https://www.youtube.com/watch?v=6ZwwapPikyQ&ab_channel=MLRecords" , #samay samjayegaa
        "https://www.youtube.com/watch?v=8-E1LbChJ88&ab_channel=ZeeMusicCompany"  , # playlist
        
        
        
    ],
    "negative": [
        "https://www.youtube.com/watch?v=Ij-xEfzOJv0&ab_channel=Release-Topic", #kitda navyane
       "https://www.youtube.com/watch?v=xdN2gYjcWuM&ab_channel=ZeeMusicMarathi", 
       "https://www.youtube.com/watch?v=EiiOYwqk3A0&ab_channel=AdityaRikhari"  , #fasle 
       "https://www.youtube.com/watch?v=pTnWKvslwDU&ab_channel=ZeeMusicCompany"
       "https://www.youtube.com/watch?v=w8FPG38BN3U&ab_channel=AmitVedwal" , #mashup
       "https://www.youtube.com/watch?v=aRw-mn4XIGk&ab_channel=YRFMusic" , #mashup yrf 
      ### "https://www.youtube.com/watch?v=2axZD58LjkM&ab_channel=Lo-fi2307" , 
       "https://www.youtube.com/watch?v=wEeGqTpM1Dw&ab_channel=%C3%81k%C3%84llr%C5%8D%C3%BB%C3%B1d%C3%AArVl%C3%B4g"
       
       
      
    ],
     "gym": [
        "https://www.youtube.com/watch?v=YqeW9_5kURI",  # Lean On
       "https://www.youtube.com/watch?v=8afBXZawfQw&ab_channel=ZeeMusicCompany",
       "https://www.youtube.com/watch?v=skhUNWhX2UY&ab_channel=OnlyMOTIVATION"
       "https://www.youtube.com/watch?v=Rnc1y_TYFpc&ab_channel=dobwen" , # zoro
       "https://www.youtube.com/watch?v=xc55HjLRZfQ&ab_channel=MVSTERIOUS-Topic" , #slava funk
       "https://www.youtube.com/watch?v=jMfvlh0tjyo&ab_channel=ZeeMusicCompany"
       "https://www.youtube.com/watch?v=g62J-8nV5FI&list=PLsL3bAY1alnf3rttdBTiyRumwZA-EoDLO&index=20&ab_channel=ZeeMusicCompany"
       
       
       
    ]
}

def get_youtube_url(mood):
    return random.choice(youtube_songs[mood])

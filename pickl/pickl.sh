#!/bin/bash
#runs the python code with the appropriate parameters

filename=picklme.py
flag1=-text
#arg1="Hello Irene, Orestis, and Pat"
#arg1="There's a huge chicken in my living room. Another sentence!"
#arg1="Hi can not make the game. There are three options. I wish to get rid of one."
arg1="As we begin entering the holiday season (!!!) it's great to remember everything we're thankful for! Unfortunately, there a lot of people in the Upper Valley area who are in need of basic necessities, such as warm clothes and food. Dartmouth Christian Union's community service team is raising money for Salvation Army's Star Tree program. Through this program, we'll be able to provide gifts for the families we have adopted. We are also providing an incentive to participate in the fundraiser! We will be raffling off two Dartmouth sweatshirts and and an EBA's pizza at the end of the fundraiser to three lucky winners!!! Although this fundraiser is being run through Christian Union, the Salvation Army's Star Tree does not discriminate towards families on the basis of religion or beliefs. Therefore, we encourage EVERYONE to donate! Your contribution is both meainingful and extremely important. You can find more information on the GOFUNDME page:"
flag2=-c
arg2=../CorpusFolder/
flag3=-tagged
arg3=True

time python $filename $flag1 "$arg1" $flag2 $arg2 $flag3 $arg3

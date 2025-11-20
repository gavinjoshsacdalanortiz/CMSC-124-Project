Test Case 1: Missing HAI
lolcodeI HAS A x ITZ 5
KTHXBYE


Test Case 2: Missing KTHXBYE
lolcodeHAI
I HAS A x ITZ 5
VISIBLE x

Test Case 3: Undeclared Variable
lolcodeHAI
VISIBLE x
KTHXBYE

Test Case 4: Wrong Operator Syntax
lolcodeHAI
I HAS A result ITZ SUM OF 2 3
KTHXBYE

Test Case 5: Loop Name Mismatch
lolcodeHAI
I HAS A i ITZ 0
IM IN YR loop UPPIN YR i TIL BOTH SAEM i AN 5
    VISIBLE i
IM OUTTA YR wrongname
KTHXBYE

Test Case 6: Function Not Found
lolcodeHAI
I IZ unknown MKAY
KTHXBYE

Test Case 7: Wrong Number of Arguments
lolcodeHAI
HOW IZ I greet YR name
    VISIBLE "Hello " name
IF U SAY SO

I IZ greet YR "Alice" AN YR "Bob" MKAY
KTHXBYE
@ECHO OFF
setlocal enableExtensions enableDelayedExpansion

SET /A X = 1

GOTO :loop


:loop
    echo start loop func 

    IF %X% EQU 1 (

        echo start loop

        python runbot.py 

        SET /p texte=< data\reboot.txt

        IF "%texte%"=="1" (
            echo eql 1
            SET /A X = 1
            ECHO 0 > data\reboot.txt 
        ) ELSE (
            echo eql 0
            echo "%texte%"
            SET /A X = 0
        )

        TIMEOUT 5 /nobreak > NUL

        echo %X%

        GOTO :loop
    )

ENDLOCAL

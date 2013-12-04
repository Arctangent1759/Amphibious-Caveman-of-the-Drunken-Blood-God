while [ 0 ]
do
if [[ $(python capture.py -b myTeam -r baselineTeam -q | tail -1 | egrep -o '(Red)|(Blue)' | grep 'Blue') ]]; then echo "Win"; else echo "Loss"; fi
if [[ $(python capture.py -r myTeam -b baselineTeam -q | tail -1 | egrep -o '(Red)|(Blue)' | grep 'Red') ]]; then echo "Win"; else echo "Loss"; fi
done

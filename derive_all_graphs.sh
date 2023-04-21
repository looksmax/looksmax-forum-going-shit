
export PYTHONPATH=$PYTHONPATH:"$PWD"

cd ./derive_metrics || exit

for f in *.py
do
  python3 "$f"
done

cd ../

import argparse, json, time
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

ROOT = Path(__file__).resolve().parent
FEATURES = ["previous_marks","internal_marks","assignment_score","attendance","practical_marks","project_score","study_hours","participation","backlogs","assignment_completion","department"]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True)
    parser.add_argument("--target",default="performance_category")
    args=parser.parse_args()
    df=pd.read_csv(args.input)
    if args.target not in df: raise SystemExit(f"Missing target column: {args.target}")
    usable=[c for c in FEATURES if c in df.columns]
    if not usable: raise SystemExit("No recognized feature columns found. See data/README.md.")
    df=df[usable+[args.target]].dropna(subset=[args.target])
    X=df[usable]; y=df[args.target].astype(str)
    if y.nunique()<2: raise SystemExit("At least two target classes are required.")
    if y.value_counts().min()<2: raise SystemExit("Each target class needs at least two rows for stratified splitting.")
    categorical=[c for c in usable if X[c].dtype=="object"]
    numeric=[c for c in usable if c not in categorical]
    prep=ColumnTransformer([
        ("num",Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),
        ("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),categorical)
    ])
    models={
        "Logistic Regression":LogisticRegression(max_iter=1500,class_weight="balanced"),
        "Decision Tree":DecisionTreeClassifier(max_depth=6,class_weight="balanced",random_state=42),
        "Random Forest":RandomForestClassifier(n_estimators=250,class_weight="balanced",random_state=42),
        "Gradient Boosting":GradientBoostingClassifier(random_state=42)
    }
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    results=[]; best=None
    for name,est in models.items():
        pipe=Pipeline([("preprocess",prep),("model",est)])
        start=time.time(); pipe.fit(Xtr,ytr); elapsed=time.time()-start
        pred=pipe.predict(Xte)
        p,r,f,_=precision_recall_fscore_support(yte,pred,average="weighted",zero_division=0)
        row={"model":name,"accuracy":accuracy_score(yte,pred),"precision_weighted":p,"recall_weighted":r,"f1_weighted":f,"training_seconds":round(elapsed,3),"confusion_matrix":confusion_matrix(yte,pred,labels=sorted(y.unique())).tolist(),"labels":sorted(y.unique())}
        results.append(row)
        if best is None or f>best[0]: best=(f,name,pipe)
    joblib.dump({"pipeline":best[2],"features":usable,"target":args.target,"model_name":best[1]},ROOT/"student_success_model.joblib")
    payload={"selected_model":best[1],"metrics":results,"note":"Held-out test metrics only describe this supplied dataset; they are not proof of real-world validity."}
    (ROOT/"metrics.json").write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))
if __name__=="__main__": main()

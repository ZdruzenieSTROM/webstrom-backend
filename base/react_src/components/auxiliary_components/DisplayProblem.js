import React from "react";
import Mathjax from "../LatexElement";

export const DisplayProblemSrc = (props) => {
  return (
    <div className="problem">
      <div className="problem-header">
        Séria {props.series} Úloha {props.problemOrder}
        <div className="btn-floating btn-small" onClick={props.handleUp}>
          <i className="material-icons">arrow_upward</i>
        </div>
        <div className="btn-floating btn-small" onClick={props.handleDown}>
          <i className="material-icons ">arrow_downward</i>
        </div>
      </div>
      <div className="problem-body">
        <div className="row">
          <form className="col s12">
            <div className="row">
              {props.showSrc ? (
                <div className="input-field col s12">
                  <textarea
                    id={"textarea-problem-" + props.problemId}
                    className="materialize-textarea"
                    value={props.text}
                    onChange={props.handleChange}
                  ></textarea>
                  <label htmlFor={"textarea-problem-" + props.problemId}>Textarea</label>
                </div>
              ) : (
                <div className="problem-tex">This is a MathJax version of the proiblem</div>
              )}
              <Mathjax text={props.text}> Some text </Mathjax>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export const DisplayProblemTeX = (props) => {
  return <div>Problem TeX</div>;
};

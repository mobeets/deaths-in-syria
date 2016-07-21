function fitToContainer(canvas, parent){
  canvas.width  = parent.width();
  canvas.height = parent.height();
}

$( document ).ready(function() {
    g = new Dygraph(

        // containing div
        document.getElementById("graphdiv"),
        "data/counts.csv",
        {
          // rollPeriod: 0,
          // showRoller: true,
        }
    );
    fitToContainer($('#graphdiv'), $('.canvas-parent'));
});

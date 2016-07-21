function fitToContainer(canvas, parent){
  canvas.width  = parent.width();
  canvas.height = parent.height();
}

$( document ).ready(function() {
    g = new Dygraph(

        // containing div
        document.getElementById("graphdiv"),
        "data/counts.csv",
        // "data/deaths-in-syria.csv",
        {
          rollPeriod: 30,
          showRoller: true,
        }
    );
    fitToContainer($('#graphdiv'), $('.canvas-parent'));
});

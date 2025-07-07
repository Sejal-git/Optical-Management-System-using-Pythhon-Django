
function pp(){
val= parseFloat(document.getElementById("FrameCount1").value) *  parseFloat(document.getElementById("PurchasePrice1").value);
document.getElementById("TotalPurchase1").value=val;

}

function tp(){
    val2=parseFloat(document.getElementById("FrameCount1").value) *  parseFloat(document.getElementById("AssignedPrice1").value);
    document.getElementById("TotalAssigned1").value=val2;
}



function rp(){
    val3=parseFloat(document.getElementById("SellingPrice").value) -  parseFloat(document.getElementById("AdvancePrice").value);
    console.log(val3)
    document.getElementById("RemainingAmount").value=val3;
}


function toalSellingPrice(){
    val4=parseFloat(document.getElementById("FramePrice").value) +  parseFloat(document.getElementById("LensPrice").value);
    console.log(val4)
    document.getElementById("SellingPrice").value=val4;
}



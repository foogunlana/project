var bParam ;
var dpVariables = {};
function DealPlySkinCls() {
	dpQuery.ajaxSetup({
	  cache: true
	});
	this.readyIntervalID = undefined;
	this.intervalID = undefined;
	dpQuery.holdReady(true);
	var path = window.location.pathname;
	this.name = path.replace(".html","").replace("/","");
	this.dealplyStarted = false;
	bParam = getURLHashParameter('b');
	this.handleServedbyCache();	
}

var getURLHashParameter = function(name) {
    return decodeURIComponent((new RegExp('[#|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.hash)||[,""])[1].replace(/\+/g, '%20'))||null;
};

function dpPopulate(data){	
	dpVariables = data;	
	try{
		dpVariables.origOffCount = dpVariables.dealsJson.length;
	} catch(e1){
		dpVariables.origOffCount = 0;
	}
	try{
		removeUninstall();
	}
	catch(e){}
	dealPlySkinObj.start();
}

DealPlySkinCls.prototype.handleServedbyCache = function(){
	//obj = this;
	dpQuery.getScript(decodeURIComponent(bParam),function(data2, textStatus2, jqxhr2) {
		//obj.start();			
	});
};

DealPlySkinCls.prototype.initDefaultSkin = function(){
	dpVariables.skin = {
			toastHeight:'143px',
			botLeftBorderRad:0,
			dealplyToastWidthInteger:29,
			dealplyFlightWidthInteger:26,
			showLngTtl:true,
			moreStrCss:''
		};

		dpVariables.skin.readyFunc = function(){
			if (!dpVariables.bStyle && dpVariables.extType===-1 && dealPlyUtils.feed === 'kpt'){
				dpQuery('#flach').addClass('kptBnr');
				dpQuery('#logoBnr').attr('src','/resources/eden/green/strip/kpt.png');
			}
		};
};

DealPlySkinCls.prototype.start = function(){
	var name = this.name; 
	dpVariables.self = "dealply-toast[src*='" +name +	"']";
	
	if(typeof dpVariables.gotoHtml == "object" && typeof dpVariables.productID == "object"){
		dpQuery(dpVariables.gotoHtml).each(function(index, value){
			if(value.search(name)>=0){
				var id = undefined;
				if(typeof dpVariables.productID[index] == 'string'){
					id = dpVariables.productID[index].trim();
				}
				dpVariables.productIDself = id;
			}
		});		
	}

	this.startDealply();	
};

DealPlySkinCls.prototype.setMessages = function(elementSelector) {
	if (window.addEventListener) { // all browsers except IE before version 9
		window.addEventListener("message", OnMessage, false);
	} else {
		if (window.attachEvent) { // IE before version 9
			window.attachEvent("onmessage", OnMessage);
		}
	}	
};
DealPlySkinCls.prototype.removeMessages = function(elementSelector) {
	if (window.removeEventListener) { // all browsers except IE before version 9
		window.removeEventListener("message", OnMessage, false);
	} else {
		if (window.detachEvent) { // IE before version 9
			window.detachEvent ("onmessage",OnMessage); 
		}
	}	
};


var OnMessage = function(event) {
	var msg = event;
	if (typeof msg !== "function" && typeof msg !== "object") {
		return;
	}

	if (msg === null) {
		return;
	}

	var msgObj = msg.data;
	if (typeof msgObj === "string" && msgObj != null) {
		try {
			if (msgObj.indexOf("d=") === 0) {
				msgObj = msgObj.substring(2);

				//msgObj = DealPlyBase64.decode(msgObj);
			} else {
				return;
			}
		} catch (dealplyE43) {

		}

		try {
			msgObj = DealPlyJSON.parse(msgObj);
		} catch (dealplyE6) {

		}
	}

	if (typeof msgObj.dealplyOrigin === "undefined" || msgObj.dealplyOrigin === null || msgObj.dealplyOrigin !== "DP-TOP") {
		return;
	}

	if (typeof msgObj.dealplyTopic === "string" && msgObj.dealplyTopic !== null && msgObj.dealplyTopic === "RPT-CLK") {
		if (typeof msgObj.dealplyEval === "object" && typeof msgObj.dealplyEval.position !== 'undefined' && typeof msgObj.dealplyEval.index !='undefined') {
			dealPlyUtils.gotoDeal(msgObj.dealplyEval.index, msgObj.dealplyEval.position);
			if(typeof msgObj.dealplyEval.gourl === 'string'){
				window.open(msgObj.dealplyEval.gourl,"_blank");
			}
		}
	}
};

function removeUninstall(){
	var partnerToRemove = ['futuin','fututb','fututw','futuft'];
	try {
	if (partnerToRemove.indexOf(dpVariables.partner) >= 0) {
		dpQuery('#dpSuspendUninstall').hide();
	}
} catch (e){}
}
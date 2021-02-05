


var menuItem = {
    "id":"amaze",
    "title":"Amaze",
    "contexts" : ["selection"]

};
chrome.contextMenus.create(menuItem);

function fixedEncodeURI (str) {
    return encodeURI(str).replace(/%5B/g, '[').replace(/%5D/g, ']');

}

chrome.contextMenus.onClicked.addListener(function(clickData){


    if (clickData.menuItemId == "amaze" && clickData.selectionText ){
        var amazeUrl = "https://www.amazon.in/s?k=" + fixedEncodeURI(clickData.selectionText);
        var createData = {
            "url" : amazeUrl,

        };
        chrome.tabs.create(createData, function(){})
    }
});
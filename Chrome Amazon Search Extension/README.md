# Amaze
#### Video Demo:  https://youtu.be/eS31flBUZpk
#### Description: A chrome extension that allows a user to search for items on amazon from any web page

##### Use Case
When a user is browsing the web and often has to search for an item they read about on another site, they first need to navigate the website and then search for the item.
Omnibox in chrome shortens this process by allowing the user to search directly from the address bar. However this still involves typing the item and then searching thus it still invovles a few steps.

Amaze is a chrome extension that allows a user to search on amazon quickly from any webpage.
The user simply needs to highlight the text they want to search, right-click and select Amaze from the list.
This automatically opens a new tab and shows the search results for the searched string, thus involving only 3 clicks and no typing.

This is an events extension that runs only when a specific event occurs.

##### Manifest
To create a chrome extension we need to first crearte a manifest.json file.
We first specify what version of the manifest we are using. Here we are currently using manifest version 2.

This file describes to the browser what the extension does. Here we first describe the name of the extension.
We also write the version number of our project.
Then we write what the extension does. This is what will appear to the user when they load the extension.
We also can add icons to the extension as it will apear in the extensions page or the toolbar.
For this we need 3 sizes of icons.
128x128, 48x48 and 16x16. 3 icons for this project have been created and are in the same project folder.

These icons created are then described in the manifest.json to tell the browser to use them as icons.
We also define what type of extension it is.
For this extension we need to run it in the background script.
In the manifest file we also describe the javascript file where we have written the code for the extension under "background".
We've written our code in the eventPage.js file.
Since we don't need to run it at all times we set "persistent" to false.

In the manifests file we also need to define what permissions are needed from the user to run the extension.
For this extension we need permissions for openinging a new tab and for creating a new item in contextMenus.

##### Eventpage javascript
In the eventPage.js we define how the extension would work.

We first create an object that will hold data related to the new menu item.
Here we define the id for the menuitem so that we can use it in functions later, the title as it will appear in the context menu, and the behaviour of the menu item.
Then we create the menu item in the chrome contextmenu by passing the object containing the name contexts and id for the menu item to chrome.contextMenus.create().

We know that texts can contain characters that are now allowed on urls. Hence we need to clean the text before we pass that onto our function.
For this we crete a new function called fixedEncodeURI. This function takes a string and removes all spaces.
It is then passed on to the javascript function encodeURI which encodes special characters in the string and returns the final URI.

We then add a listener using the chrome API to listen for any clicks.
We use chrome.contextMenus.onClicked.addListener for this.
We then describe an anonymous funcion inside it with the clickdata captured.

We use a if condition to check if our extension was selected from the context menu.
Simuiltaneously we also check if there was some text that was selected when the click event happened.
If both these things are true we create a new variable "amazeUrl" that appends the selected string to the amazon search url.
This variable is then added to the object "createData".
The object is then passed on to chrome.tabs.create() which then creates a new tab and visits the url in the object passed onto it.
Thus our extension then opens the amazon page we the search results for the highlighted text.
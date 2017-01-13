/* MATERIAL DESIGN ALPHABET IN CSS/JS
 * Script by Nicolas Mougin http://mougino.free.fr
 * Freely modifiable under GNU GPL v3 licence https://www.gnu.org/licenses/gpl.txt
 */

var special = 'efhix347'; // these letters are composed of 2 parts
var numbers = '1234567890';

// first: parse and replace content of 'material' containers
var e = document.getElementsByClassName('material');
while (e[0]) {
  var txt = e[0].textContent;
  var scale = parseFloat(e[0].getAttribute('scale'));
  var h = document.createElement('div'); // replacement DOM
  h.className = 'container' + (e[0].className.indexOf('centered') > -1 ? ' centered' : '');
  if (scale > 0) h.setAttribute('scale', scale);
  for (var j=0; j < txt.length; j++) {
    var letter = txt[j].toLowerCase();
    var d2 = document.createElement('div');
    d2.className = (numbers.indexOf(letter) > -1 ? 'nb' : '') + letter;
    var d1 = document.createElement('div');
    d1.className = 'alphabet';
    d1.appendChild(d2);
    if (-1 != special.indexOf(letter)) { // draw other half of special letters
      var d2bis = document.createElement('div');
      d2bis.className = (numbers.indexOf(letter) > -1 ? 'nb' : '') + letter + '-half';
      d1.appendChild(d2bis);
    }
    h.appendChild(d1);
  }
  e[0].parentNode.replaceChild(h, e[0]);
  e = document.getElementsByClassName('material'); // iterate by re-scanning modified DOM for 'material'
}

// second: scale/center each resulting 'container' div
e = document.getElementsByClassName('container');
for (i = 0; i < e.length; i++) {
  var scale = parseFloat(e[i].getAttribute('scale'));
  if (scale) {
    var h = 100 * scale; // actual container height after scaling
    var letters = parseInt(e[i].childElementCount);
    var ow = 100 * letters; // original container width
    e[i].style.transform = 'scale(' + scale + ')';
    e[i].style['-webkit-transform'] = 'scale(' + scale + ')';
    if (e[i].className.indexOf('centered') == -1) {
      e[i].style['transform-origin'] = '0 0';
      e[i].style['-webkit-transform-origin'] = '0 0';
      e[i].style.width = ow + 'px';
    }
    e[i].style.height = h + 'px';
  }
}

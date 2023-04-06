/*alert("bonjour")*/
const my_func = () =>{ /*permet que ça ne soit pas run à chaque fois qu'on charge la page mais pour que ça soit run il faut taper my_func() dans la console */
    const searchfield = document.querySelectorAll('#domain_filter')[0]
    searchfield.addEventListener('input', (e)=>{
        let line = document.querySelectorAll('tbody tr')
        for (let i = 0; i < line.length; i++) {
            if (line[i].cells[1].outerText.search(e.target.value)==-1){
                line[i].style.display='none'
            } else{
                line[i].style.display='table-row'
            }
        }})
}

const highlight = () =>{
    const list_prot = document.querySelectorAll('#proteins tbody tr')
    const list_domain = document.querySelectorAll('#related tbody tr')
    const enter_prot=()=>{
        for (let i = 0; i <list_prot.length; i++){
            list_prot[i].addEventListener('mouseenter',()=>{
                list_prot[i].classList.add("highlight")
                for (let j=0; j<list_domain.length;j++){
                    if (list_prot[i].classList.contains(list_domain[j].id)){
                        list_domain[j].classList.add("highlight")}
                    }
            })
        }
    }

    const leave_prot=()=>{
        for (let i = 0; i <list_prot.length; i++){
            list_prot[i].addEventListener('mouseleave',()=>{
                list_prot[i].classList.remove("highlight")
                for (let j=0; j<list_domain.length;j++){
                    if (list_prot[i].classList.contains(list_domain[j].id)){
                        list_domain[j].classList.remove("highlight")}
                    }
             })
        }
    }

    const enter_domain=()=>{
        for (let i = 0; i <list_domain.length; i++){
            list_domain[i].addEventListener('mouseenter',()=>{
                list_domain[i].classList.add("highlight")
                for (let j=0;j<list_prot.length;j++){
                    if (list_prot[j].classList.contains(list_domain[i].id)){
                        list_prot[j].classList.add("highlight")
                    }
                }
            })
        }
    }

    const leave_domain=()=>{
        for (let i = 0; i <list_domain.length; i++){
            list_domain[i].addEventListener('mouseleave',()=>{
                list_domain[i].classList.remove("highlight")
                for (let j=0;j<list_prot.length;j++){
                    if (list_prot[j].classList.contains(list_domain[i].id)){
                        list_prot[j].classList.remove("highlight")
                    }
                }
            })
        }
    }

    enter_prot()
    leave_prot()
    enter_domain()
    leave_domain()
}

const setToolTips=()=>{
    const line_related=document.querySelectorAll("#related tbody tr")
    for (let i = 0; i <line_related.length; i++){
        short = line_related[i].children[1]
        short.addEventListener('click',()=>{
            fetch("/domains/"+line_related[i].id.toString()+".json")
            .then((resp) => {
                if (!resp.ok) { throw("Error " + resp.status); }
                return resp.json();
            }).then((data) => {
                alert(data['description'])
            }).catch((err) => {
                console.error(err);
            });
        })

    }
}
/* pour tester rapidement : console directement sur navigateur (click droit puis inspecter puis console)
document est le premier noeud du document après head ou body 
document.querySelectorAll('div') : select tous les trucs div
on peut stocker la valeur dans let ou cons
let my_node = document.querySelectorAll('div')[1] (on a noeud 1)
*.addEventListener('event', (truc ano)=>{console.log("coucou:")})
node.addEventListener('click', (e)=>{console.dir(e)}) 
lorsqu'on clique ça affiche :
click { target: main#content.main-content
, buttons: 0, clientX: 1191, clientY: 168, layerX: 1191, layerY: 168 }
altKey: false
bubbles: true
button: 0
buttons: 0
cancelBubble: false
cancelable: true
clientX: 1191
clientY: 168
composed: true
ctrlKey: false
currentTarget: null
defaultPrevented: false
detail: 1
eventPhase: 0
explicitOriginalTarget: <main id="content" class="main-content  ">
isTrusted: true
layerX: 1191
layerY: 168
metaKey: false
movementX: 0
movementY: 0
mozInputSource: 1
mozPressure: 0
offsetX: 0
offsetY: 0
originalTarget: <main id="content" class="main-content  ">
pageX: 1191
pageY: 168
rangeOffset: 0
rangeParent: null
region: ""
relatedTarget: null
returnValue: true
screenX: 1191
screenY: 287
shiftKey: false
srcElement: <main id="content" class="main-content  ">​
target: <main id="content" class="main-content  ">
​timeStamp: 706845
​type: "click"
​view: Window https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import
​which: 1
​x: 1191
​y: 168
​<get isTrusted()>: function isTrusted()
​<prototype>: MouseEventPrototype { initMouseEvent: initMouseEvent(), getModifierState: getModifierState(), initNSMouseEvent: initNSMouseEvent(), … }

const searchfield = document.querySelectorAll('#domain_filter')[0]
searchfield.addEventListener('input', (e) => {})

*/

<template>
    <div id="footer">
        <div class="row">
            <div class="col-12">
                <ul class="logos-footer">
                    <li id="footer-cgi">
                        <a href="https://cgi.br"></a>
                    </li>
                    <li id="footer-nic">
                        <a href="https://nic.br"></a>
                    </li>
                    <li id="footer-registro" class="d-none d-md-block">
                        <a href="https://registro.br"></a>
                    </li>
                    <li id="footer-cert" class="d-none d-md-block">
                        <a href="https://cert.br"></a>
                    </li>
                    <li id="footer-cetic" class="d-none d-md-block">
                        <a href="https://cetic.br"></a>
                    </li>
                    <li id="footer-ceptro" class="d-none d-md-block">
                        <a href="https://ceptro.br"></a>
                    </li>
                    <li id="footer-ceweb" class="d-none d-lg-block">
                        <a href="https://ceweb.br"></a>
                    </li>
                    <li id="footer-ix" class="active">
                        <a href="https://ix.br"></a>
                    </li>
                    <li id="footer-w3c" class="d-none d-lg-block">
                        <a href="https://www.w3c.br/Home/WebHome"></a>
                    </li>
                </ul>
            </div>
        </div>
        <div id="footer-info">
            <div class="col col-12">
                <div class="row">
                    <div class="col-lg-4 col-md-10 offset-md-2">
                        <p>
                            NIC.BR - Núcleo de Informação e Coordenação do Ponto BR
                            <br> CNPJ: 05.506.560/0001-36
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
#footer {
    background: #353535;
    clear: both;
    margin-top: 50px;
    float: left;
    width: 100%;
}

#footer-info {
    color: #757575;
    font-size: 11px;
    background: #242424;
    height: 75px;
    padding-top: 20px;
}

.logos-footer {
    display: inline;
}

.logos-footer a {
    display: inline-block;
    background-image: url(../assets/footer.png);
    background-repeat: no-repeat;
}

.logos-footer li {
    display: inline-block;
    border-bottom: 1px solid #4A4A4A;
    border-right: 1px solid #4A4A4A;
    float: left;
    height: 120px;
    margin-bottom: 16px;
    margin-top: 40px;
    padding-left: 2%;
}

.logos-footer li.active {
    /*    background-image: url(/assets/orange.png);
    background-repeat: repeat-x;
    background-position: bottom;*/
    border-bottom-color: #D37E3F;
    border-bottom-width: 9px;
}

#footer-cgi {
    background: #2E2E2E;
    border: medium none;
    margin-top: 0;
    margin-bottom: 0;
    padding-left: 3%;
    padding-top: 40px;
    height: 220px;
    width: 14%;
    min-width: 95px;
}

#footer-cgi a {
    margin-top: 8px;
    background-position: 0 -515px;
    height: 72px;
    width: 78px;
}

#footer-nic {
    width: 13%;
    min-width: 100px;
    padding-left: 2%;
    border-right: 1px solid #4A4A4A;
}

#footer-nic a {
    margin-top: 8px;
    background-position: 0 -760px;
    height: 83px;
    width: 84px;
}

#footer-registro {
    width: 12%;
    min-width: 111px;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
}

#footer-registro a {
    background-position: 0 -978px;
    height: 45px;
    width: 95px;
}

#footer-cert {
    width: 8%;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
    min-width: 78px;
}

#footer-cert a {
    background-position: 0 -195px;
    height: 48px;
    width: 63px;
}

#footer-cetic {
    width: 9%;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
    min-width: 85px;
}

#footer-cetic a {
    background-position: 0 -313px;
    height: 45px;
    width: 71px;
}

#footer-ceptro {
    width: 11%;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
    min-width: 105px;
}

#footer-ceptro a {
    background-position: 0 -74px;
    height: 48px;
    width: 89px;
}

#footer-ceweb {
    width: 11%;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
}

#footer-ceweb a {
    background-position: 0 -358px;
    height: 47px;
    width: 85px;
}

#footer-ix {
    width: 10%;
    min-width: 85px;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px
}

#footer-ix a {
    background-position: 0 -587px;
    height: 47px;
    width: 75px;
}

#footer-w3c {
    width: 7%;
    padding-left: 1%;
    height: 100px;
    margin-top: 60px;
}

#footer-w3c a {
    background-position: 0 -1082px;
    height: 32px;
    width: 47px;
}

#footer-trabalhe {
    display: inline-block;
    border: none;
    margin-left: 20px;
    height: 40px;
}

#footer-trabalhe a {
    font-size: 13px;
    color: #D4753A;
    margin-right: 15px;
}
</style>

<template>
    <header role="banner">
        <div class="row">
            <div class="col-md-4 col-xs-8">
                <img src="../assets/logo-ix-br.png" alt="Logo Nic.br / Ix.br">
                <a href="https://nic.br" id="link-nic" style="background: url(about:blank)">&nbsp;</a>
                <a href="https://ix.br" id="link-ix" style="background: url(about:blank)">&nbsp;</a>
            </div>
            <div class="col-md-8 hidden-sm hidden-xs text-right">
                <div class="language-top pull-right">
                    <a href="#">Trocar idioma
                        <b>PT</b>
                    </a>
                    <a href="#">Change language
                        <b>EN</b>
                    </a>
                </div>

                <div class="header-buttons">
                    <button class="btn btn-light">
                        <span>Logout</span>
                    </button>
                </div>
            </div>
        </div>

        <div class="row third-line">
            <div class="col-md-12">
                <nav class="navbar navbar-expand-lg navbar-dark navbar-inverse mb-4">
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false"
                        aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link ml-3" href="/painel">Dashboard</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link ml-3" href="/pttlogin/mysettings.php">My Account</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link ml-3" href="/recommendations">Recommendations</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link ml-3" href="/looking-glass">BGP Looking Glass</a>
                            </li>
                            <li class="nav-item">
                                <a class="active nav-link ml-3" href="#">Invoice</a>
                            </li>
                        </ul>
                    </div>
                </nav>
            </div>
        </div>
    </header>
</template>

<style type="text/scss" scoped>
    .language-top {
        padding: 10px 0 10px;
        width: 100%;
    }
    .language-top a {
        color: #000
    }
    .language-top a:first-child:after {
        content: "";
        width: 1px;
        height: 24px;
        color: #fff;
        display: inline-block;
        position: relative;
        top: 10px;
        margin: 0 5px
    }
    .navbar-inverse {
        background-color: #222;
        border-color: #080808
    }
    nav {
        border-radius: 4px;
    }
    #link-nic, #link-ix {
        display: block;
        float: left;
        position: absolute;
        text-decoration: none;
    }
    #link-nic {
        height: 34px;
        left: 24px;
        top: 25px;
        width: 75px;
    }
    #link-ix {
        height: 75px;
        left: 107px;
        top: 15px;
        width: 111px;
    }
    nav a.active {
        color: #EDEDED;
        font-weight: bold;
    }
</style>

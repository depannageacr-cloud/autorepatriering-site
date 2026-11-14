<?php
declare(strict_types=1);
ini_set('session.use_strict_mode', '1');
session_set_cookie_params(['secure'=>true,'httponly'=>true,'samesite'=>'Lax','path'=>'/']);
session_start();
header('Cache-Control: no-store');
header('X-Robots-Tag: index, follow');
if (empty($_SESSION['token'])) { $_SESSION['token']=bin2hex(random_bytes(32)); $_SESSION['opened']=time(); }
$error=''; $sent=false;
$limits=['naam'=>120,'email'=>254,'telefoon'=>50,'wagen'=>350,'tijd'=>200,'bericht'=>5000];
$values=[];
foreach ($limits as $key=>$max) { $v=$_POST[$key]??''; $values[$key]=is_string($v)?trim($v):''; }
function h(string $text): string { return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
if ($_SERVER['REQUEST_METHOD']==='POST') {
    $token=$_POST['token']??'';
    if (!is_string($token) || !hash_equals($_SESSION['token'], $token) || !empty($_POST['website'])) {
        $error='Uw aanvraag kon niet worden verwerkt. Herlaad de pagina en probeer opnieuw.';
    } elseif (time()-(int)($_SESSION['opened']??time())<3) {
        $error='Controleer uw gegevens en probeer over enkele seconden opnieuw.';
    } elseif (time()-(int)($_SESSION['last_sent']??0)<60) {
        $error='Uw vorige aanvraag is net verzonden. Wacht even voordat u opnieuw verzendt.';
    } else {
        foreach ($limits as $key=>$max) { if (strlen($values[$key])>$max*4) { $error='Een veld is te lang. Kort uw bericht in.'; } }
        foreach (['naam','email','bericht'] as $key) { if ($values[$key]==='') { $error='Vul naam, e-mail en uw transportvraag in.'; } }
        if (!filter_var($values['email'], FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n]/', $values['email'])) { $error='Vul een geldig e-mailadres in.'; }
        if ($error==='') {
            $labels=['naam'=>'Naam','email'=>'E-mail','telefoon'=>'Telefoon','wagen'=>'Voertuiggegevens','tijd'=>'Gewenst moment','bericht'=>'Transportvraag'];
            $body="Nieuwe aanvraag via autorepatriering.be\n\n";
            foreach ($labels as $key=>$label) { $body.=$label.": ".($values[$key]!==''?$values[$key]:'Niet opgegeven')."\n\n"; }
            $headers="From: ACR Voertuigtransport <website@autorepatriering.be>\r\nReply-To: ".$values['email']."\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8";
            if (mail('depannageacr@hotmail.com','Nieuwe transportaanvraag - autorepatriering.be',$body,$headers)) {
                $_SESSION['last_sent']=time(); $_SESSION['token']=bin2hex(random_bytes(32)); $sent=true; $values=array_fill_keys(array_keys($limits),'');
            } else { $error='Verzenden lukt momenteel niet. Uw aanvraag is niet verzonden. Bel ACR Voertuigtransport of gebruik WhatsApp hieronder.'; }
        }
    }
    if ($error!=='') { http_response_code(422); }
}
?>

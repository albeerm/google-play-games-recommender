"""
Pipeline para construir datasets de videojuegos desde Google Play Store
========================================================================
Dataset 1: Información de juegos válidos (sin duplicados)
Dataset 2: Interacciones jugador-juego-rating para Recommender System
"""

import time
import random
import pandas as pd
from google_play_scraper import app, reviews, Sort
from google_play_scraper.exceptions import NotFoundError
from collections import defaultdict

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
MIN_REVIEWS_PER_PLAYER = 5   # Un jugador debe tener al menos N opiniones
REVIEWS_PER_GAME       = 1000  # Cuántas reviews descargar por juego (ajusta según necesidad)
LANG                   = "es"
COUNTRY                = "es"
DELAY_BETWEEN_CALLS    = (1.0, 2.5)  # Segundos aleatorios entre llamadas (evitar ban)

# ─────────────────────────────────────────────
# TU LISTA DE IDs (puede tener duplicados y IDs inválidos)
# ─────────────────────────────────────────────
RAW_GAME_IDS = [
    "ai.character.app",
    "air.com.bmapps.gossipgirlsdivasinhighschool",
    "air.com.buffalo_studios.newflashbingo",
    "air.com.flipline.papascheeseriatogo",
    "air.com.flipline.papascluckeriatogo",
    "air.com.flipline.papasdonuteriatogo",
    "air.com.flipline.papasmochariatogo",
    "air.com.flipline.papaspancakeriahd",
    "air.com.flipline.papaspancakeriatogo",
    "air.com.flipline.papaspizzeriatogo",
    "air.com.flipline.papassushiriatogo",
    "air.com.flipline.papaswingeriatogo",
    "air.com.goodgamestudios.empirefourkingdoms",
    "air.com.hypah.io.slither",
    "air.com.littlebigsnake.littlebigsnake",
    "air.com.noxgames.PuppetSoccer2014",
    "air.com.pixelfederation.diggy",
    "air.com.playtika.cvs",
    "air.com.playtika.slotomania",
    "air.com.qublix.forestrescue",
    "air.com.sgn.cookiejam.gp",
    "air.com.sgn.cookiejamblast.gp",
    "air.com.sgn.juicejam.gp",
    "air.com.sticksports.sticktennis",
    "air.origami.diagram",
    "aliens.zombies.invasion",
    "and.brainworks.holeemall",
    "and.lihuhu.tilesinhole",
    "app.alo.yoga.aloyoga.shoppings",
    "app.gotall.play",
    "app.jumpjumpvpn.jumpjumpvpn",
    "app.loopad.loopad",
    "app.otbo5ly",
    "app.protectsmartly.bb2fe610e54446cebdf627db55227d7d",
    "ata.squid.kaw",
    "ata.strike.puzzle.diamond.paint.jam",
    "azurgames.idle.war",
    "ball.sort.puzzle.color.sorting.bubble.games",
    "ball.sort.water.color.hoop.stack.puzzle",
    "beatmaker.edm.musicgames.pianofire2",
    "beats.color.sing.star.rush",
    "bible.wordgame.words.connect.crossword.cookies",
    "biggiant.prisonescape",
    "block.puzzle.sudoku.free.game.classic.offline",
    "blockpuzzle.wood.sudoku.puzzlegames",
    "br.com.w12.vitastudio",
    "bubbleshooter.orig",
    "ca.dominospizza",
    "camera.seissiger.notify",
    "ch.hbenecke.sunday",
    "ch.protonvpn.android",
    "chessfriends.online.chess",
    "co.courseplay.menalearning",
    "co.hodor.uzpoe",
    "co.jarvis.rghv",
    "co.tapcart.app.id_4AdiiuTvtb",
    "co.tapcart.app.id_BrDtBG7PIX",
    "co.thefab.tm",
    "color.by.number.coloring.paint.puzzle.pixel.art.drawing.painting.games.kids.adults.fun.pictures",
    "color.paint.by.number.pgmaker",
    "com.AlfaBravo.CombatMaster",
    "com.Astroolee.Anno117FanGuide",
    "com.BallGames.Woodturning",
    "com.Boardible.Boardible",
    "com.Cerberus.StreetDrag2",
    "com.ChetanSurpur.Orbit",
    "com.DGSWTeamSSR.JUSTJUMP",
    "com.Deroxisstudio.AsteroidHunter",
    "com.DreamonStudios.BladesofDeceron",
    "com.EagleEyeGames.KeeponMining",
    "com.Earthkwak.Platformer",
    "com.EraFlip.BusEscapeParkingJamGame",
    "com.EraFlip.FlappyCloudy",
    "com.EternalStudio.SurvivorZ",
    "com.FireproofStudios.TheRoom",
    "com.FireproofStudios.TheRoom2",
    "com.FireproofStudios.TheRoom4",
    "com.GacoGames.EC2",
    "com.Gaggle.fun.GooseGooseDuck",
    "com.Giganticduck.Bombergrounds",
    "com.HFG.EnigmaFables",
    "com.HoYoverse.Nap",
    "com.HoYoverse.hkrpgoversea",
    "com.InlogicSports.FootballKicks",
    "com.InlogicSports.MiniSoccerKick",
    "com.JindoBlu.OfflineGames",
    "com.KhoGames.WarzoneCommander",
    "com.Kidoverse.HairSalon",
    "com.Laxarus.TigerBall",
    "com.Love.Story",
    "com.Love.Story.Games.ChatLinx",
    "com.Love.Story.Games.Kissed.Billionaire",
    "com.LudoStar2GameLudoGameYallaLudoGame",
    "com.MarisSoftware.CarsLP",
    "com.MiaoYou.RabbitBubbleShooter",
    "com.MonsterPlanet.BlockDay",
    "com.NeverGames.Gridpunk",
    "com.Nobodyshot.kuboom",
    "com.OctocubeGamesCompany.CIFI",
    "com.RastleksGames.MergeFighters",
    "com.RayGaming.JellyJump",
    "com.SeePlay.SurvivalEscape",
    "com.Seeplay.BanaToon",
    "com.Seriously.BestFiends",
    "com.Shooter.ModernWarfront",
    "com.VRStudio.catchup",
    "com.VisualConcepts.MyNBA2K",
    "com.WalkTalk.FlightMaster",
    "com.YovoGames.taxi2",
    "com.Zgame.BallSort",
    "com.aboveai.aboveai",
    "com.activision.callofduty.shooter",
    "com.adengames.grasssurfer",
    "com.adsk.sketchbook",
    "com.adventurer.adventurer",
    "com.aeropdf.img2pdf",
    "com.agminstruments.drumpadmachine",
    "com.aidiangames.gossipgirl.gp",
    "com.aidiangames.masterchecf.gp",
    "com.aigrind.skylore",
    "com.aim.racing",
    "com.air.hockey.glow.hd",
    "com.alice.games.summer.friends",
    "com.alien.shooter.galaxy.attack",
    "com.amanotes.beathopper",
    "com.amanotes.pamadancingroad",
    "com.amelosinteractive.snake",
    "com.americasbestpics",
    "com.and.games505.TerrariaPaid",
    "com.andymstone.sunposition",
    "com.andymstone.sunpositiondemo",
    "com.animal.hunter.sniper",
    "com.anon.dev.spell",
    "com.ansangha.dr1010",
    "com.ansangha.drdriving",
    "com.ansangha.drjb",
    "com.ansangha.drparking4",
    "com.ansangha.drpipe2",
    "com.appfactory.incomeflow",
    "com.appgp.crw",
    "com.apple.android.music",
    "com.apple.bnd",
    "com.application.pokecardex",
    "com.appsomniacs.mmc",
    "com.aqupepgames.projectpepe",
    "com.arcade.mine",
    "com.archery.king.game",
    "com.arketa.sculptwithmk",
    "com.arkgames.ggplay.rodna",
    "com.arkgames.ggplay.tlonglobal",
    "com.artifexmundi.mopa1.gp",
    "com.asharinfotech.catalogmaker",
    "com.astropaycard.android",
    "com.asyncstudio.knifethrower",
    "com.atomic.lovelife",
    "com.avidionmedia.iGun2",
    "com.axlebolt.standoff2",
    "com.azgame.app.poolcity",
    "com.azure.authenticator",
    "com.azurgames.stackball",
    "com.backflipstudios.android.dragonvale",
    "com.backflipstudios.transformersearthwars",
    "com.bag.farm.day.village.farming.games",
    "com.bambuna.podcastaddict",
    "com.bamnetworks.mobile.android.gameday.atbat",
    "com.bandagames.mpuzzle.gp",
    "com.bandainamcoent.dbgekishinsquadra",
    "com.bandainamcoent.dblegends_ww",
    "com.bandainamcoent.hiroacawwus",
    "com.bandainamcoent.opbrww",
    "com.bandainamcoent.ultimateninjastorm",
    "com.bandainamcogames.dbzdokkan",
    "com.bandainamcogames.dbzdokkanww",
    "com.bentostudio.ballsvsblocks",
    "com.bestplay.app",
    "com.bethsoft.stronghold",
    "com.bfa.battlelines",
    "com.bgg.jump",
    "com.bgs.grandmafia.openworld.gangster.crime",
    "com.bigbluebubble.singingmonsters.full",
    "com.bigblueparrot.pokerfriends",
    "com.bigduckgames.flow",
    "com.bigideagames.googleplay.superhockey",
    "com.biglime.cookingmadness",
    "com.bitmango.rolltheballunrollme",
    "com.bkdevs.async",
    "com.blackcircleapps.wonderlandbingo",
    "com.blackout.blackjack",
    "com.blackout.bubble",
    "com.blackout.gin",
    "com.blackout.spades",
    "com.blizzard.diablo.immortal",
    "com.blizzard.messenger",
    "com.blizzard.wtcg.hearthstone",
    "com.block.game.jigsaw.puzzles",
    "com.block.juggle",
    "com.block.puzzle.crush.magic.game",
    "com.blockpuzzlegame.sudokublock.woodpuzzle",
    "com.boddle.learning",
    "com.bombayplay.CardCrack",
    "com.boombitgames.Dartsy",
    "com.boxitsoft.battleofwizards",
    "com.budgestudios.StrawberryShortcakeBakeShare",
    "com.budgestudios.googleplay.FrozenFRZ",
    "com.budgestudios.googleplay.TransformersDisasterDash",
    "com.builder.craft3d",
    "com.bunbunstudio.magicblocktiles",
    "com.cassette.aquapark",
    "com.catdaddy.cat22",
    "com.catdaddy.nba2km",
    "com.chennaigames.mrracer.premium",
    "com.chess",
    "com.chess.chesscoach",
    "com.chess.strategy.boardgame",
    "com.chillingo.robberybob2.android.gplay",
    "com.chownow.kinjasushi",
    "com.chrome.beta",
    "com.chrystianvieyra.physicstoolboxsuite",
    "com.city.building.master",
    "com.clickteam.ultimatecustomnight",
    "com.clogica.audiomerger",
    "com.club.mobile.android",
    "com.codigames.idle.barber.shop.empire.tycoon",
    "com.codigames.idle.prison.empire.manager.tycoon",
    "com.colgate.humkids",
    "com.color.blast.match.game",
    "com.color.blast.puzzle.quest",
    "com.color.blast.shooter",
    "com.com2us.smon.normal.freefull.google.kr.android.common",
    "com.combo.matcher",
    "com.comunix.pokerface",
    "com.cookapps.bm.fortresssaga",
    "com.cookapps.wonder.merge.dragon.magic.evolution.merging.wondermerge",
    "com.cooking.chaos.restaurant.games",
    "com.cooking.kitchen.madness.supermarket.game",
    "com.cookingcity.chef.kitchen.craze.fever",
    "com.countystory.mergecooking",
    "com.crazygames.crazygamesapp",
    "com.creations.runnergame",
    "com.creditkarma.mobile",
    "com.critical.strike2",
    "com.criticalforceentertainment.criticalops",
    "com.crossword.bible.cookies.find.english",
    "com.crowdstar.covetfashion",
    "com.crunchyroll.gv.kawaiikitchen.game",
    "com.crystal.usad",
    "com.customuse.customuse",
    "com.cuteu.videochat",
    "com.d3p.mpq",
    "com.daerisoft.thespikerm",
    "com.dcjnmed.jifqq",
    "com.denachina.g63002013.android",
    "com.desireapps.desire",
    "com.devhz.humzabaan",
    "com.dhigamesstudio.chickensway.puzzlegame",
    "com.dhigamesstudio.gemjam.puzzlegame",
    "com.dialekts.snake.game",
    "com.dialekts.sort.juice",
    "com.dialekts.sortballs",
    "com.dig.deep",
    "com.digitaldash.whiplash",
    "com.dirtybit.fire",
    "com.disney.emojimatch_goo",
    "com.disney.frozensaga_goo",
    "com.disney.maleficent_goo",
    "com.distinctivegames.hockeyallstars2",
    "com.distinctivegames.rugbyleague24",
    "com.distinctivegames.rugbynations24",
    "com.distinctivegames.rugbynations26",
    "com.diveomedia.little.stories.bedtime.books.kids",
    "com.dkxqzbfkjt.pocketchess",
    "com.dominos.sa",
    "com.dominospizza",
    "com.dopuz.klotski.riddle",
    "com.downdogapp",
    "com.dps.prison.escape.obbybreakout",
    "com.dream.free.games.match3",
    "com.dreamgames.royalkingdom",
    "com.dreamgames.royalmatch",
    "com.drjimcostello.balance",
    "com.droidhang.slot.android.google",
    "com.dropbox.android",
    "com.druryoutdoors.deercast.app",
    "com.dsd164.snake97",
    "com.dts.freefiremax",
    "com.dts.freefireth",
    "com.dumyah.partners_app",
    "com.duolingo",
    "com.dvbarannik.operation.nightfall",
    "com.dxl.android",
    "com.dxx.firenow",
    "com.ea.game.nfs14_row",
    "com.ea.game.pvz2_na",
    "com.ea.game.pvz2_row",
    "com.ea.game.pvzfree_row",
    "com.ea.game.simcitymobile_row",
    "com.ea.game.starwarscapital_row",
    "com.ea.games.nfs13_na",
    "com.ea.games.simsfreeplay_row",
    "com.ea.gp.connect",
    "com.ea.gp.fifamobile",
    "com.ea.gp.nbamobile",
    "com.earlymorningstudio.trident",
    "com.easybrain.jigsaw.puzzles",
    "com.einnovation.temu",
    "com.epicgames.fortnite",
    "com.episodeinteractive.android.catalog",
    "com.ericcbm.snake",
    "com.evodefensetd.gp",
    "com.exapp.zzap",
    "com.extremedevelopers.wingsofwar",
    "com.extremedevelopers.wwr",
    "com.facebook.orca",
    "com.fcmtravel.android",
    "com.feedhenry.fhLaya",
    "com.ffsvideogames.aab.btaw5f2p",
    "com.fluffyfairygames.idleminertycoon",
    "com.fulldive.extension.launcher",
    "com.fungames.sniper3d",
    "com.funtomic.matchmasters",
    "com.gameloft.android.ANMP.GloftA8HM",
    "com.gameloft.android.ANMP.GloftGGHM",
    "com.gameloft.android.ANMP.GloftM5HM",
    "com.gangverk.sling",
    "com.gbgengine.puyoonline",
    "com.getos1.driver",
    "com.glennvillebank.mobile",
    "com.globle.app214867",
    "com.google.android.apps.adm",
    "com.google.android.apps.subscriptions.red",
    "com.google.android.apps.walletnfcrel",
    "com.google.android.apps.youtube.music",
    "com.google.android.deskclock",
    "com.google.android.googlequicksearchbox",
    "com.google.android.play.games",
    "com.google.android.projection.gearhead",
    "com.groplay.abcalfons",
    "com.h8games.helixjump",
    "com.hackensack.myhmh",
    "com.halfbrick.brickwars",
    "com.halfbrick.dantheman",
    "com.halfbrick.fruitninjafree",
    "com.heytap.headset",
    "com.hit.master",
    "com.hopesteps.app",
    "com.hritwik.avoid",
    "com.hyperbeard.odyssey",
    "com.hyperhitter.android",
    "com.ibm.events.android.masters",
    "com.ifs.banking.fiid6008",
    "com.igg.android.doomsdaylastsurvivors",
    "com.igg.android.mythicheroes",
    "com.imangi.templerun2",
    "com.inside.towelie",
    "com.instagram.android",
    "com.instarunners",
    "com.ionz.omnimatrix",
    "com.ironhidegames.android.kingdomrushorigins",
    "com.italankin.fifteen2",
    "com.jumpgames.rswrb",
    "com.justapps.fdmanager",
    "com.kabam.marvelbattle",
    "com.kayac.mannequinDownhill",
    "com.kayac.numbermergerun",
    "com.kaypora.fireup.app",
    "com.kelly.ktbsonline",
    "com.keplerians.icescream",
    "com.ketchapp.pineapplepen",
    "com.ketchapp.rush",
    "com.ketchapp.twist",
    "com.king.candycrush4",
    "com.king.diamonddiariessaga",
    "com.koalitygame.hoopland",
    "com.krsna",
    "com.kwgames.packagefactory",
    "com.lego.legobuildinginstructions",
    "com.levelinfinite.sgameGlobal",
    "com.lithiosapps.coworks.biolabs",
    "com.lszenlamzr.parkingjam",
    "com.lucky.zootchi",
    "com.ludia.tmnt",
    "com.lukedoukakis.speedstars",
    "com.m3as.timemanagement",
    "com.madness.combat",
    "com.mapmyrun.android2",
    "com.marianatek.latinasweatproject",
    "com.mattel.hwcollector",
    "com.matteljv.uno",
    "com.mcdonalds.app",
    "com.mediasolutionscorp.storeapp.bens",
    "com.meesho.supply",
    "com.mergecorp.merge",
    "com.miHoYo.bh3global",
    "com.miaoyou.bouncingball",
    "com.michaelbegelspacher.mbmethodebegelspacher",
    "com.microdose.balljam",
    "com.microminimice.idleballescape",
    "com.microsoft.copilot",
    "com.microsoft.emmx",
    "com.microsoft.loop",
    "com.microsoft.office.outlook",
    "com.miniclip.eightballpool",
    "com.mizmowireless.acctmgt",
    "com.mobile.legends.usa",
    "com.mobirix.airhockey",
    "com.mojang.minecraftpe",
    "com.musictap.musictap_mobile",
    "com.mvizlab.lucy.android.en",
    "com.mxy.photo.ai",
    "com.ndemiccreations.afterinc",
    "com.nebula.mahjongtile",
    "com.nekki.shadowfightarena",
    "com.netease.eggypartyen",
    "com.netease.g108na",
    "com.netflix.NGP.AsphaltXtreme",
    "com.netlinkvoice.connectmobile",
    "com.netqin.ps",
    "com.newyes.notenew",
    "com.nflystudio.InfiniteStaircase",
    "com.nintendo.zaka",
    "com.noodlecake.ssg4",
    "com.noracavani.albahealth",
    "com.nutritionix.nixtrack",
    "com.onebiteapps.nycsubwaytracker",
    "com.ourpalm.kof98.us",
    "com.outfit7.talkingben",
    "com.outfit7.talkingtomgoldrun",
    "com.outsystemsenterprise.ppp.OSSApp",
    "com.oxiwyle.modernage2",
    "com.parallels.client",
    "com.pazugames.avatarworld",
    "com.phasesapp",
    "com.phototime.membership",
    "com.pikpok.hrc.play",
    "com.pitch.track_a_pitch",
    "com.pixel.art.coloring.color.number",
    "com.pixonic.wwr",
    "com.planetfitness",
    "com.playdigious.deadcells.mobile",
    "com.playgendary.sportmasters",
    "com.playrix.township",
    "com.playstack.balatro.android",
    "com.playtika.wsop.gp",
    "com.portonics.mygp",
    "com.productmadness.cashmancasino",
    "com.pronetis.ironball2",
    "com.propel.ebenefits",
    "com.proximabeta.aoemobile",
    "com.psamarine.ohs",
    "com.pushscheduler",
    "com.reddit.frontpage",
    "com.rghvsapp.android.sosalert",
    "com.rigpa.missioncit_nremt",
    "com.riotgames.league.wildrift",
    "com.roblox.client",
    "com.robtopx.geometryjumplite",
    "com.rockstar.gta3",
    "com.rockstargames.gtavc",
    "com.rousoftware.donttap",
    "com.rovio.baba",
    "com.scribble.thesuitch",
    "com.sdmcsoftware.quizomg",
    "com.sega.sonicboomandroid",
    "com.senspark.goldminerclassic",
    "com.shaverma.lazyjump",
    "com.shoprrewards.app",
    "com.simplepractice.clients",
    "com.sixtemia.ib2seguretat",
    "com.snapchat.android",
    "com.sosalert.app",
    "com.soulvenworks.thatsnotmyneighbor",
    "com.speed.drivengo",
    "com.spypoint.spypointApp",
    "com.stonegolemstudios.CombatWear2",
    "com.superbox.aos.brickbreaker",
    "com.supercell.clashofclans",
    "com.supercell.hayday",
    "com.swingbyswing",
    "com.tapblaze.coffeebusiness",
    "com.telmate.TelmateGettingout",
    "com.temenosDream.temenosDream",
    "com.tencent.ig",
    "com.tencent.mhadv",
    "com.tfgco.games.sports.free.tennis.clash",
    "com.tgc.sky.android",
    "com.trainerize.getitwrightfitness",
    "com.trochoi.swipebrick",
    "com.tubitv",
    "com.ultimate.myth.rebirth",
    "com.ultimatecheerdance.icp",
    "com.unicostudio.braintest",
    "com.upfaithandfamily",
    "com.usanetwork.watcher",
    "com.vamapps.thecoach",
    "com.venturesis.miniclash",
    "com.vgames.thefallingball",
    "com.vitastudio.mahjong",
    "com.vitotechnology.StarWalk2Free",
    "com.water.balls",
    "com.water.tracker.remind",
    "com.waterslide.park",
    "com.whatsapp.w4b",
    "com.whoyaho.tanghulu",
    "com.wildlifestudios.jet.airplane.games.sky.warriors",
    "com.windyty.android",
    "com.wizards.winter_orb",
    "com.wonderful.mahjong",
    "com.xiaomi.smarthome",
    "com.xsprice.nettools",
    "com.xsquarestudio.forcelte",
    "com.yum.pizzahut",
    "com.zapi.zaka",
    "com.zenoti.glomd",
    "com.zeptolab.thieves.google",
    "com.zns.app",
    "com.zynga.pottermatch",
    "ct.brickball",
    "easy.sudoku.puzzle.solver.free",
    "es.socialpoint.MonsterLegends",
    "eu.europa.ec.ecas",
    "events.grip.dcdconnect",
    "fc.pcam.me",
    "games.nerf.epic.pranks.free",
    "games.vaveda.militaryoverturn",
    "githit.game.tlmn",
    "id.kgi.mobile",
    "in.playsimple.wordsearch",
    "io.kcpay",
    "iptv.smart.xciptv.xtream.m3u.player.live.tv.channels",
    "itm.ma330.kobm",
    "jp.co.capcom.sf4ce",
    "jp.co.celsys.clipstudiopaint.googleplay",
    "jp.co.sony.ips.portalapp",
    "jp.drsv.SkateSpace",
    "jp.gocro.smartnews.android",
    "jp.konami.pesam",
    "jp.ne.ibis.ibispaintx.app",
    "linkdesks.tile.match.fun",
    "me.alicorn.epcg",
    "me.zepeto.main",
    "mobi.sevenwinds.bigsix",
    "net.dbdle.app",
    "net.defensezone3.ultra",
    "net.metro.taprider",
    "net.sharewire.parkmobilev2",
    "net.wargaming.wot.blitz",
    "nl.navara.zigzag",
    "nz.co.stuff.android.news",
    "oldringtones.forgionne.retronotificationtones",
    "org.alpha.courseapp",
    "org.bibleleague.bible.spanish",
    "org.telegram.plus",
    "paid.tester.earn.money.cash.games",
    "pe.gob.smv.smv",
    "rooms.handmadegame.net",
    "ru.sportmaster.app",
    "screw.puzzle.match3.brain.puzz",
    "solitaire.patience.card.games.klondike.free",
    "tv.remote.control.firepro",
    "us.kr.baseballnine",
    "videoeditor.videorecorder.screenrecorder",
    "vn.pancake.app",
    "volumebooster.sound.loud.speaker.booster",
    "world.fly.corp"
]
# ════════════════════════════════════════════════════════════════
# PASO 1: Deduplicar IDs
# ════════════════════════════════════════════════════════════════
def deduplicate_ids(raw_ids: list[str]) -> list[str]:
    seen = set()
    unique = []
    duplicates = []
    for gid in raw_ids:
        if gid in seen:
            duplicates.append(gid)
        else:
            seen.add(gid)
            unique.append(gid)
    print(f"[IDs] Total: {len(raw_ids)} | Únicos: {len(unique)} | Duplicados eliminados: {len(duplicates)}")
    if duplicates:
        print(f"       Duplicados: {duplicates}")
    return unique


# ════════════════════════════════════════════════════════════════
# PASO 2: Obtener metadata de cada juego (Dataset 1)
# ════════════════════════════════════════════════════════════════
def fetch_game_metadata(game_ids: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """
    Devuelve:
        - DataFrame con info de juegos válidos
        - Lista de IDs válidos (para usar en el paso siguiente)
    """
    records = []
    valid_ids = []
    invalid_ids = []

    for gid in game_ids:
        try:
            time.sleep(random.uniform(*DELAY_BETWEEN_CALLS))
            info = app(gid, lang=LANG, country=COUNTRY)
            records.append({
                "app_id":      gid,
                "title":       info.get("title"),
                "genre":       info.get("genre"),
                "url":         info.get("url"),
                "description": (info.get("description") or "").strip(),
                "score":       info.get("score"),          # Rating promedio (0–5)
                "ratings":     info.get("ratings"),        # Total de ratings
                "reviews":     info.get("reviews"),        # Total de reseñas con texto
            })
            valid_ids.append(gid)
            print(f"  ✅ {gid} → '{info.get('title')}'")

        except NotFoundError:
            invalid_ids.append(gid)
            print(f"  ❌ {gid} → No encontrado (inválido)")
        except Exception as e:
            invalid_ids.append(gid)
            print(f"  ⚠️  {gid} → Error: {e}")

    df_games = pd.DataFrame(records)
    print(f"\n[Metadata] Juegos válidos: {len(valid_ids)} | Inválidos: {len(invalid_ids)}")
    if invalid_ids:
        print(f"           IDs inválidos: {invalid_ids}")
    return df_games, valid_ids


# ════════════════════════════════════════════════════════════════
# PASO 3: Descargar reviews para cada juego (Dataset 2)
# ════════════════════════════════════════════════════════════════
def fetch_reviews(valid_ids: list[str], reviews_per_game: int = REVIEWS_PER_GAME) -> pd.DataFrame:
    """
    Descarga reviews de Google Play y construye la tabla jugador-juego-rating.
    """
    all_reviews = []

    for gid in valid_ids:
        try:
            time.sleep(random.uniform(*DELAY_BETWEEN_CALLS))
            result, _ = reviews(
                gid,
                lang=LANG,
                country=COUNTRY,
                sort=Sort.MOST_RELEVANT,
                count=reviews_per_game,
            )
            for r in result:
                all_reviews.append({
                    "player_id": r.get("userName"),   # Nombre del usuario como ID
                    "app_id":    gid,
                    "rating":    r.get("score"),      # 1–5 estrellas
                    "at":        r.get("at"),         # Fecha de la reseña
                })
            print(f"  📥 {gid} → {len(result)} reviews descargadas")

        except Exception as e:
            print(f"  ⚠️  {gid} → Error descargando reviews: {e}")

    df_raw = pd.DataFrame(all_reviews)
    print(f"\n[Reviews] Total filas brutas: {len(df_raw)}")
    return df_raw


# ════════════════════════════════════════════════════════════════
# PASO 4: Filtrar y validar Dataset 2
# ════════════════════════════════════════════════════════════════
def build_interactions_dataset(
    df_raw: pd.DataFrame,
    valid_ids: list[str],
    min_reviews_per_player: int = MIN_REVIEWS_PER_PLAYER,
) -> pd.DataFrame:
    """
    Aplica los filtros:
      1. Elimina duplicados jugador-juego (conserva la última review).
      2. Filtra jugadores con < min_reviews_per_player opiniones.
      3. Garantiza que todos los juegos válidos aparezcan al menos 1 vez.
    """
    if df_raw.empty:
        print("⚠️  No hay reviews para procesar.")
        return df_raw

    # 1. Eliminar nulos en player_id o rating
    df = df_raw.dropna(subset=["player_id", "rating"]).copy()

    # 2. Si un jugador tiene varias reviews del mismo juego, quedarse con la más reciente
    df = df.sort_values("at", ascending=False)
    df = df.drop_duplicates(subset=["player_id", "app_id"], keep="first")
    print(f"[Filtro 1] Tras eliminar duplicados jugador-juego: {len(df)} filas")

    # 3. Filtrar jugadores que tienen al menos min_reviews_per_player opiniones
    player_counts = df["player_id"].value_counts()
    valid_players = player_counts[player_counts >= min_reviews_per_player].index
    df = df[df["player_id"].isin(valid_players)]
    print(f"[Filtro 2] Jugadores con ≥{min_reviews_per_player} opiniones: {len(valid_players)} → {len(df)} filas")

    # 4. Verificar cobertura de juegos: todos deben aparecer al menos 1 vez
    games_in_dataset = set(df["app_id"].unique())
    games_all = set(valid_ids)
    missing_games = games_all - games_in_dataset

    if missing_games:
        print(f"\n⚠️  {len(missing_games)} juego(s) sin representación tras filtrar jugadores:")
        print(f"    {missing_games}")
        print("    → Re-añadiendo sus reviews (relajando el filtro de jugadores para estos juegos)...")

        # Para los juegos sin cobertura, tomamos sus reviews del df_raw original
        # y las añadimos igualmente (aunque el jugador tenga pocas reviews en total)
        df_missing = df_raw[df_raw["app_id"].isin(missing_games)].dropna(subset=["player_id", "rating"])
        df_missing = df_missing.drop_duplicates(subset=["player_id", "app_id"], keep="first")

        if not df_missing.empty:
            # Por cada juego sin cobertura, cogemos la review con el rating más alto
            # (representativa) para asegurar que aparece en el dataset
            df_missing_best = (
                df_missing.sort_values("rating", ascending=False)
                .groupby("app_id")
                .first()
                .reset_index()
            )
            df = pd.concat([df, df_missing_best], ignore_index=True)
            df = df.drop_duplicates(subset=["player_id", "app_id"], keep="first")
            print(f"    ✅ Añadidas {len(df_missing_best)} filas de respaldo. Total: {len(df)} filas")
        else:
            print("    ❌ Tampoco hay reviews disponibles para esos juegos.")
    else:
        print(f"✅ Todos los {len(valid_ids)} juegos tienen al menos 1 review en el dataset.")

    # Seleccionar columnas finales y ordenar
    df = df[["player_id", "app_id", "rating", "at"]].sort_values(["player_id", "app_id"]).reset_index(drop=True)

    return df


# ════════════════════════════════════════════════════════════════
# PASO 5: Resumen estadístico
# ════════════════════════════════════════════════════════════════
def print_summary(df_games: pd.DataFrame, df_interactions: pd.DataFrame, valid_ids: list[str]):
    print("\n" + "═"*55)
    print("  RESUMEN FINAL")
    print("═"*55)
    print(f"\n📦 Dataset 1 — Juegos")
    print(f"   Juegos válidos:     {len(df_games)}")
    print(f"   Géneros únicos:     {df_games['genre'].nunique()}")
    print(f"   Rating promedio:    {df_games['score'].mean():.2f}")

    if not df_interactions.empty:
        print(f"\n🎮 Dataset 2 — Interacciones")
        print(f"   Total filas:        {len(df_interactions)}")
        print(f"   Jugadores únicos:   {df_interactions['player_id'].nunique()}")
        print(f"   Juegos únicos:      {df_interactions['app_id'].nunique()} / {len(valid_ids)}")
        print(f"   Rating promedio:    {df_interactions['rating'].mean():.2f}")
        print(f"   Distribución de ratings:")
        for r, cnt in df_interactions["rating"].value_counts().sort_index().items():
            bar = "█" * (cnt // max(1, len(df_interactions)//50))
            print(f"     ⭐{r}: {cnt:5d}  {bar}")

        reviews_per_player = df_interactions.groupby("player_id").size()
        print(f"\n   Reviews por jugador:")
        print(f"     Min: {reviews_per_player.min()} | Max: {reviews_per_player.max()} | Media: {reviews_per_player.mean():.1f}")

        games_covered = set(df_interactions["app_id"].unique())
        missing = set(valid_ids) - games_covered
        if missing:
            print(f"\n   ⚠️  Juegos sin cobertura: {missing}")
        else:
            print(f"\n   ✅ Todos los juegos tienen cobertura.")
    print("═"*55)


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
def main():
    print("="*55)
    print("  GOOGLE PLAY GAME DATASET BUILDER")
    print("="*55)

    # Paso 1: Deduplicar IDs
    print("\n── PASO 1: Deduplicar IDs ──────────────────────")
    unique_ids = deduplicate_ids(RAW_GAME_IDS)

    # Paso 2: Metadata de juegos (Dataset 1)
    print("\n── PASO 2: Descargando metadata de juegos ───────")
    df_games, valid_ids = fetch_game_metadata(unique_ids)

    # Paso 3: Descargar reviews (para Dataset 2)
    print("\n── PASO 3: Descargando reviews ─────────────────")
    df_raw_reviews = fetch_reviews(valid_ids)

    # Paso 4: Construir Dataset 2 con filtros
    print("\n── PASO 4: Construyendo dataset de interacciones ")
    df_interactions = build_interactions_dataset(
        df_raw=df_raw_reviews,
        valid_ids=valid_ids,
        min_reviews_per_player=MIN_REVIEWS_PER_PLAYER,
    )

    # Paso 5: Resumen
    print_summary(df_games, df_interactions, valid_ids)

    # Guardar CSVs
    df_games.to_csv("dataset_games.csv", index=False)
    df_interactions.to_csv("dataset_interactions.csv", index=False)
    print("\n💾 Archivos guardados:")
    print("   → dataset_games.csv")
    print("   → dataset_interactions.csv")

    return df_games, df_interactions


if __name__ == "__main__":
    df_games, df_interactions = main()
